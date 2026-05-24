import os
import logging
import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from customer_repository import (
    get_customer_by_mitid_user_id,
    get_customer_context,
    get_customer_dashboard,
    validate_mitid_user_id,
)
from rag_pipeline import retrieve_top_chunks, build_context
from llm_provider import generate_llm_response

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)

logger = logging.getLogger("pension-ai-backend")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class ChatMessage(BaseModel):
    role: str
    content: str


class Message(BaseModel):
    message: str
    session_id: Optional[str] = None
    history: List[ChatMessage] = Field(default_factory=list)
    force_llm_fail: bool = False


class MitidLoginRequest(BaseModel):
    user_id: str


class LogoutRequest(BaseModel):
    session_id: str


SESSION_TTL_SECONDS = 75 * 60
CHAT_HISTORY_TTL_SECONDS = 30 * 60

SESSION_STORE: dict[str, dict[str, object]] = {}
CHAT_HISTORY_STORE: dict[int, dict[str, object]] = {}

RATE_LIMIT_WINDOW_SECONDS = 60
RATE_LIMIT_MAX_REQUESTS = 10
RATE_LIMIT_STORE: dict[str, list[datetime]] = {}


# ============================================================
# SESSION / CHAT HISTORY
# ============================================================


def get_session_expiry() -> datetime:
    return datetime.now(timezone.utc) + timedelta(seconds=SESSION_TTL_SECONDS)



def create_demo_session(customer_id: int) -> str:
    session_id = secrets.token_urlsafe(32)
    SESSION_STORE[session_id] = {
        "customer_id": customer_id,
        "expires_at": get_session_expiry(),
    }
    return session_id



def get_session_payload(session_id: str | None) -> dict[str, object] | None:
    if not session_id:
        return None

    session = SESSION_STORE.get(session_id)
    if not session:
        return None

    expires_at = session["expires_at"]
    if not isinstance(expires_at, datetime) or expires_at <= datetime.now(timezone.utc):
        SESSION_STORE.pop(session_id, None)
        return None

    return session



def get_customer_id_from_session(session_id: str | None) -> int | None:
    session = get_session_payload(session_id)
    if not session:
        return None

    return int(session["customer_id"])



def refresh_session(session_id: str | None) -> datetime | None:
    session = get_session_payload(session_id)
    if not session:
        return None

    expires_at = get_session_expiry()
    session["expires_at"] = expires_at
    return expires_at



def cleanup_chat_history() -> None:
    now = datetime.now(timezone.utc)

    expired_customer_ids = [
        customer_id
        for customer_id, history in CHAT_HISTORY_STORE.items()
        if history.get("expires_at") <= now
    ]

    for customer_id in expired_customer_ids:
        CHAT_HISTORY_STORE.pop(customer_id, None)



def get_saved_chat_history(customer_id: int) -> list[dict[str, str]]:
    cleanup_chat_history()

    history = CHAT_HISTORY_STORE.get(customer_id)
    if not history:
        return []

    return list(history["messages"])



def append_saved_chat_message(customer_id: int, role: str, content: str) -> None:
    cleanup_chat_history()

    history = CHAT_HISTORY_STORE.setdefault(
        customer_id,
        {
            "messages": [],
            "expires_at": datetime.now(timezone.utc)
            + timedelta(seconds=CHAT_HISTORY_TTL_SECONDS),
        },
    )

    messages = history["messages"]
    messages.append({"role": role, "content": content})

    history["messages"] = messages[-24:]
    history["expires_at"] = datetime.now(timezone.utc) + timedelta(
        seconds=CHAT_HISTORY_TTL_SECONDS
    )


# ============================================================
# RATE LIMIT
# ============================================================


def check_rate_limit(identifier: str) -> None:
    if os.getenv("DISABLE_RATE_LIMIT") == "true":
        return

    now = datetime.now(timezone.utc)
    window_start = now - timedelta(seconds=RATE_LIMIT_WINDOW_SECONDS)

    recent_requests = [
        request_time
        for request_time in RATE_LIMIT_STORE.get(identifier, [])
        if request_time > window_start
    ]

    if len(recent_requests) >= RATE_LIMIT_MAX_REQUESTS:
        logger.warning("Rate limit exceeded for identifier: %s", identifier)
        raise HTTPException(
            status_code=429,
            detail="For mange beskeder på kort tid. Prøv igen om lidt.",
        )

    recent_requests.append(now)
    RATE_LIMIT_STORE[identifier] = recent_requests


# ============================================================
# QUESTION CLASSIFICATION
# ============================================================


def classify_question(user_text: str) -> str:
    text = user_text.lower()

    complex_keywords = [
        "bør jeg",
        "skal jeg vælge",
        "skal jeg flytte",
        "skal jeg starte",
        "hvad er bedst",
        "har jeg nok pension",
        "realistisk",
        "levestandard",
        "ville du anbefale",
        "hvad ville du gøre",
        "hvis du var min rådgiver",
        "bekymret for",
        "har jeg sparet nok",
        "sparet nok op",
        "de næste 5 år",
        "næste 5 år",
        "hvad ville du konkret anbefale",
        "hvad ville du anbefale",
        "realistisk gå på pension",
        "beholde samme levestandard",
        "samme levestandard",
        "bør jeg ændre",
        "skal jeg vente",
        "tage tidlig pension",
        "har jeg nok opsparing",
        "hvor meget bør jeg indbetale",
        "bør jeg spare mere op",
        "skal jeg ændre risikoprofil",
        "skal jeg ændre investering",
        "hvad passer bedst",
        "kan det betale sig",
        "anbefaler du",
        "hvad vil du anbefale",
        "for mig",
        "min situation",
        "min opsparing er",
        "mit afkast",
        "har jeg ret til",
        "må jeg",
        "hvornår kan jeg gå på pension",
        "gå tidligere på pension",
        "tidligere på pension",
        "kan jeg gå tidligere",
        "hvad betyder det økonomisk",
        "økonomisk hvis jeg går tidligere",
        "betaler jeg nok",
        "betaler jeg for lidt",
        "indbetaler jeg nok",
        "skal jeg indbetale mere",
        "højere løn",
        "jeg har fået højere løn",
        "jeg har fået lønforhøjelse",
        "fået højere løn",
        "tjener mere",
        "ændre noget i min pension",
        "optimere min pension",
        "optimere min pensionsopsparing",
        "passer min risikoprofil",
        "højere eller lavere risiko",
    ]

    semi_keywords = [
        "samle",
        "udbetaling",
        "begunstiget",
        "begunstigelse",
        "hvad gør jeg",
        "hvad skal jeg gøre",
        "jeg er blevet",
        "jeg har fået",
        "jeg mister",
        "jeg er syg",
        "jeg er blevet syg",
        "alvorligt syg",
        "alvorlig sygdom",
        "sygdom",
        "syg",
        "skifter job",
        "nyt job",
        "arbejdsløs",
        "arbejdslos",
        "selvstændig",
        "selvstaendig",
        "går ned i tid",
        "gaar ned i tid",
        "fleksjob",
        "skilt",
        "skilsmisse",
        "separeret",
        "børn",
        "boern",
        "kræft",
        "kraeft",
        "diagnose",
        "kritisk sygdom",
        "tab af erhvervsevne",
        "erhvervsevne",
        "død",
        "doed",
        "afdød",
        "afdoed",
        "min mand er død",
        "min kone er død",
        "min ægtefælle er død",
        "min partner er død",
    ]

    if any(keyword in text for keyword in complex_keywords):
        return "complex"

    if any(keyword in text for keyword in semi_keywords):
        return "semi"

    return "simple"



def needs_customer_data(user_text: str) -> bool:
    text = user_text.lower()

    personal_keywords = [
        "mit afkast",
        "min begunstigelse",
        "min begunstiget",
        "min begunstigede",
        "hvem er min begunstigede",
        "hvem er begunstiget",
        "hvem får min pension hvis jeg dør",
        "hvem får min pension, hvis jeg dør",
        "mine forsikringer",
        "hvor meget har jeg",
        "hvad har jeg stående",
        "hvor meget har jeg stående",
        "har jeg stående",
        "jeg har fået højere løn",
        "jeg har fået lønforhøjelse",
        "hvor meget står der",
        "hvad står der på min pension",
        "hvor meget har jeg sparet op",
        "hvor meget har jeg sparet",
        "hvad er min månedlige indbetaling",
        "min månedlige indbetaling",
        "mine månedlige indbetalinger",
        "hvad indbetaler jeg",
        "hvor meget indbetaler jeg",
        "hvor meget betaler jeg",
        "min indbetaling",
        "mine indbetalinger",
        "betaler jeg nok",
        "indbetaler jeg nok",
        "skal jeg indbetale mere",
        "min pensionsopsparing",
        "min opsparing",
        "min risikoprofil",
        "hvilke forsikringer har jeg",
        "hvad er jeg dækket af",
        "hvilke dækninger har jeg",
        "mine dækninger",
        "min pension investeret",
        "min pension er investeret",
        "hvordan er min pension investeret",
        "hvilke pensioner har jeg",
        "hvilke pensionsordninger har jeg",
        "mine pensionsordninger",
        "mine pensioner",
        "hvad får jeg udbetalt",
        "hvor meget får jeg udbetalt",
        "min udbetaling",
        "min forventede udbetaling",
        "mine omkostninger",
        "min pal-skat",
        "min skattekode",
        "hvad er min skattekode",
        "min løn",
        "højere løn",
        "fået højere løn",
        "jeg tjener",
        "tjener mere",
        "kan jeg gå tidligere",
        "gå tidligere på pension",
        "hvad betyder det økonomisk",
        "hvad vil det betyde økonomisk",
        "min pension hvis jeg bliver syg",
        "min pension hvis jeg bliver alvorligt syg",
        "hvis jeg bliver alvorligt syg",
    ]

    return any(keyword in text for keyword in personal_keywords)



def is_general_death_or_beneficiary_question(user_text: str) -> bool:
    text = user_text.lower()

    general_patterns = [
        "hvem får min pension, hvis jeg dør",
        "hvem får min pension hvis jeg dør",
        "hvem får pensionen hvis jeg dør",
        "hvem får pengene hvis jeg dør",
        "hvad sker der med min pension hvis jeg dør",
        "hvad sker der med min pension, hvis jeg dør",
    ]

    return any(pattern in text for pattern in general_patterns)



def requires_personal_assessment(user_text: str) -> bool:
    text = user_text.lower()

    assessment_keywords = [
        "bør jeg",
        "skal jeg vælge",
        "skal jeg flytte",
        "skal jeg starte",
        "hvad er bedst",
        "hvad passer bedst",
        "for mig",
        "har jeg nok pension",
        "har jeg nok opsparing",
        "realistisk",
        "levestandard",
        "hvad ville du gøre",
        "hvis du var min rådgiver",
        "bekymret for",
        "ville du anbefale",
        "min situation",
        "kan det betale sig",
        "gå tidligere på pension",
        "tidligere på pension",
        "kan jeg gå tidligere",
        "har jeg sparet nok",
        "sparet nok op",
        "de næste 5 år",
        "næste 5 år",
        "hvad ville du konkret anbefale",
        "hvad ville du anbefale",
        "realistisk gå på pension",
        "beholde samme levestandard",
        "samme levestandard",
        "hvad betyder det økonomisk",
        "anbefaler du",
        "hvad vil du anbefale",
        "har jeg ret til",
        "hvornår kan jeg gå på pension",
        "betaler jeg nok",
        "indbetaler jeg nok",
        "skal jeg indbetale mere",
        "højere løn",
        "fået højere løn",
        "tjener mere",
        "ændre noget i min pension",
        "optimere min pension",
        "passer min risikoprofil",
    ]

    return any(keyword in text for keyword in assessment_keywords)



def is_closing_message(user_text: str) -> bool:
    normalized = user_text.lower().strip()

    closing_messages = {
        "tak",
        "tak!",
        "mange tak",
        "tusind tak",
        "fedt tak",
        "perfekt tak",
        "super tak",
        "okay tak",
        "tak for hjælpen",
        "tak for det",
        "det var alt",
        "ellers tak",
        "nej tak",
        "fint tak",
        "cool tak",
        "super",
        "perfekt",
        "fedt",
        "nice",
        "ok",
        "okay",
    }

    return normalized in closing_messages



def is_in_scope_question(user_text: str) -> bool:
    text = user_text.lower()

    pension_domain_keywords = [
        "pension",
        "ratepension",
        "livrente",
        "livsvarig",
        "aldersopsparing",
        "folkepension",
        "atp",
        "anbefale",
        "anbefaling",
        "konkret anbefale",
        "hvad ville du anbefale",
        "hvad ville du konkret anbefale",
        "næste 5 år",
        "de næste 5 år",
        "gøre de næste",
        "prioritere",
        "fokusområde",
        "fokusområder",
        "rådgivning",
        "seniorpension",
        "førtidspension",
        "foertidspension",
        "tidlig pension",
        "arne-pension",
        "pensionsalder",
        "pensionsopsparing",
        "opsparing",
        "udbetaling",
        "indbetaling",
        "fradrag",
        "skat",
        "pal",
        "pensionsafkastskat",
        "afkast",
        "investering",
        "risiko",
        "risikoprofil",
        "modregning",
        "begunstiget",
        "begunstigelse",
        "dødsfald",
        "doedsfald",
        "dør",
        "død",
        "doed",
        "afdød",
        "afdoed",
        "pårørende",
        "paaroerende",
        "arv",
        "testamente",
        "samlever",
        "ægtefælle",
        "forsikring",
        "forsikringer",
        "dækning",
        "dækninger",
        "kritisk sygdom",
        "alvorligt syg",
        "alvorlig sygdom",
        "tab af erhvervsevne",
        "erhvervsevne",
        "kræft",
        "kraeft",
        "diagnose",
        "sygdom",
        "syg",
        "sygemeldt",
        "fleksjob",
        "arbejdsløs",
        "arbejdslos",
        "selvstændig",
        "selvstaendig",
        "nyt job",
        "skifter job",
        "højere løn",
        "løn",
        "skilt",
        "skilsmisse",
        "separeret",
        "børn",
        "boern",
        "måned",
        "om måneden",
        "pensam",
        "rådgiver",
        "kontakt",
        "stående",
        "sparet op",
    ]

    return any(keyword in text for keyword in pension_domain_keywords)



def is_obviously_out_of_scope(user_text: str) -> bool:
    return not is_in_scope_question(user_text)


# ============================================================
# PROMPT
# ============================================================


SYSTEM_PROMPT = """
Du skriver som en erfaren pensionsrådgiver med 15+ års erfaring.

Din stil er:
- rolig
- konkret
- prioriterende
- analytisk
- ikke undervisende
- ikke chatbot-agtig

Du må kun svare ud fra den kontekst, du får udleveret.
Hvis kundedata indeholder relevante oplysninger, skal du bruge dem aktivt.

Hvis KUNDEDATA giver et rimeligt grundlag,
skal du forsøge at give en konkret vejledende vurdering.

Manglende detaljer må ikke automatisk føre til:
"Det fremgår ikke af mit datagrundlag."

Brug de oplysninger der faktisk findes.

Sig kun:

"Det fremgår ikke af mit datagrundlag."

hvis centrale oplysninger mangler, så spørgsmålet ikke kan besvares meningsfuldt.

Du må ikke gætte eller bruge viden uden for konteksten.
Du må ikke opfinde kundedata, der ikke står i KUNDEDATA.
KUNDEDATA er den primære sandhed for kundens egne tal.
Hvis der står en samlet pensionsopsparing i KUNDEDATA, skal du bruge dette tal som sandhed.
Du må ikke selv opfinde, sammenlægge eller ændre kundens tal.
Du må kun lave simple beregninger, hvis du tydeligt viser beregningen og bruger tal direkte fra KUNDEDATA.

Ved spørgsmål som "bør jeg", "hvad anbefaler du", "hvad er smartest" eller "hvad skal jeg gøre", må du ikke give en endelig personlig anbefaling.
Du må gerne give en vejledende vurdering baseret på kundedata.
Brug formuleringer som:
"Ud fra dine oplysninger peger det på..."
"Det vil være relevant at undersøge..."
"Et fornuftigt næste skridt kan være..."

Svar altid på dansk.
Svar skal være lette at læse visuelt.

Brug struktur når spørgsmålet er personligt eller komplekst.

Du må bruge:
- korte overskrifter
- korte afsnit
- punktopstillinger
- nummererede næste skridt

Du må IKKE skrive én lang tekstblok.

Formatér især komplekse/personlige svar som en rådgiver-opsummering.

Du håndterer to typer spørgsmål:
1. First-level generelle pensionsspørgsmål.
2. Personlige overbliksspørgsmål, når kundedata er tilgængelige.

Ved generelle spørgsmål:
- svar neutralt
- brug kun generel pensionsviden
- undgå "hos os" eller "PenSam", medmindre spørgsmålet handler om PenSam-handlinger

Ved komplekse/personlige svar:

Når KUNDEDATA findes:

START altid analysen i KUNDEDATA.

Brug konkrete kundetal aktivt.

Besvar ikke spørgsmålet generelt først.

Svar først på:

"Hvad betyder kundens konkrete situation?"

før du forklarer generelle regler.

Brug markdown-format.

Brug gerne:

### Overskrift

tekst

### Overskrift

- punkt
- punkt

### Næste skridt

1. ...
2. ...
3. ...

Svar skal ligne et professionelt rådgivningsmøde-notat.

Undgå store tekstblokke.

Hold sektionerne korte og tydelige.

- brug konkrete tal fra KUNDEDATA
- skriv som en erfaren pensionsrådgiver i et rådgivningsmøde
- skriv naturligt og forklarende
- prioriter kundens vigtigste 2-4 forhold
Vælg aktivt de mest betydningsfulde observationer fra kundedata.

Ikke alle data er lige vigtige.

Spørg dig selv:

"Hvis jeg sad i et rigtigt rådgivningsmøde — hvad ville jeg være mest opmærksom på hos denne kunde?"

Prioritér derefter svaret.

- fremhæv hvad der er mest relevant i netop kundens situation
- undgå at gennemgå alle mulige pensionsemner
- undgå punkt-for-punkt rapportstil
- forklar tallene i almindeligt sprog
- prioriter de 2-4 vigtigste pointer fremfor lange lister
- vær konkret og analytisk
- undgå lange generelle forklaringer
- forklar hvad tallene betyder for kunden
- fokuser på de vigtigste konsekvenser
- giv højst 2-3 korte næste skridt

skriv typisk 120-250 ord.

Korte spørgsmål:
50-120 ord.

Komplekse/personlige spørgsmål:
120-250 ord.

Undgå at forklare mere end nødvendigt.
Svar skal føles som et effektivt rådgivningsmøde — ikke som en rapport.

Stop når kundens vigtigste beslutningspunkter er forklaret.

- stop når de vigtigste pointer er forklaret
- undgå at gentage kundedata flere gange
- Skriv altid dine svar som en pensionsrådgiver, der forklarer og rådgiver, ikke som en FAQ-side eller en chatbot
- afslut med et kort forbehold, hvis valget afhænger af kundens situation
- hold fokus på brugerens konkrete spørgsmål
- introducer ikke ekstra pensionsordninger eller regler,
  medmindre de er direkte relevante

Du må gerne give en vejledende vurdering baseret på kundedata.
Du må ikke give bindende økonomisk, juridisk eller skattemæssig rådgivning.
Du må ikke beslutte for kunden.
Du må ikke anbefale én endelig løsning som den eneste rigtige.

Du må gerne give tydelige prioriterede anbefalinger,
hvis KUNDEDATA giver et rimeligt grundlag.

Brug formuleringer som:

"Jeg ville især overveje..."
"Det mest oplagte fokusområde ser ud til at være..."
"Hvis målet er X, peger dine data især på..."

Undgå at blive unødigt passiv.

Hvis konkrete tal findes i KUNDEDATA:

brug dem præcist.

Opfind aldrig alternative beløb.

Gentjek tal før du svarer.

Hvis et spørgsmål handler om optimering, tidligere pension, højere løn, indbetaling, investering eller risikoprofil:
- forklar kundens nuværende situation ud fra KUNDEDATA
- forklar hvilke forhold kunden bør overveje
- sig ikke kun "kontakt en rådgiver"
- brug rådgiver-henvisningen som afslutning, ikke som hele svaret

Ved handlinger, fx sygdom, dødsfald, samle pension, ændre begunstigelse eller kontakt:
- forklar hvad situationen typisk betyder
- brug kundedata, hvis de er relevante
- giv konkrete trin
- du må skrive "hos PenSam" og "kontakt os", hvis det understøttes af konteksten

Hvis brugeren spørger:

- hvad du ville være mest bekymret for
- hvad du ville anbefale
- hvad der bør prioriteres
- hvad der bør gøres de næste år

så skal du agere som en erfaren pensionsrådgiver.

Prioritér aktivt de vigtigste 1-3 fokusområder.

Undgå neutrale ikke-svar.

"""


# ============================================================
# ROUTES
# ============================================================


@app.get("/")
def root():
    return {"status": "Backend kører"}


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "pension-ai-backend",
        "sessions_active": len(SESSION_STORE),
        "chat_histories_active": len(CHAT_HISTORY_STORE),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


@app.post("/mitid/resolve-user")
def resolve_mitid_user(request: MitidLoginRequest):
    try:
        customer = get_customer_by_mitid_user_id(request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Fejl ved MitID-opslag")
        raise HTTPException(status_code=500, detail=str(e))

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Bruger-ID blev ikke fundet i demo-databasen.",
        )

    return {"customer": customer}


@app.post("/mitid/complete-login")
def complete_mitid_login(request: MitidLoginRequest):
    try:
        customer = get_customer_by_mitid_user_id(request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.exception("Fejl ved MitID-login")
        raise HTTPException(status_code=500, detail=str(e))

    if customer is None:
        raise HTTPException(
            status_code=404,
            detail="Bruger-ID blev ikke fundet i demo-databasen.",
        )

    session_id = create_demo_session(customer["customer_id"])
    expires_at = get_session_payload(session_id)["expires_at"]

    return {
        "session_id": session_id,
        "expires_at": expires_at.isoformat(),
        "ttl_seconds": SESSION_TTL_SECONDS,
        "customer": customer,
    }


@app.post("/mitid/validate-user-id")
def validate_mitid_user(request: MitidLoginRequest):
    try:
        validate_mitid_user_id(request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"valid": True}


@app.post("/logout")
def logout(request: LogoutRequest):
    SESSION_STORE.pop(request.session_id, None)
    return {"logged_out": True}


@app.post("/session/refresh")
def refresh_login_session(request: LogoutRequest):
    expires_at = refresh_session(request.session_id)

    if expires_at is None:
        raise HTTPException(
            status_code=401,
            detail="Sessionen er ikke gyldig. Log ind igen.",
        )

    return {
        "expires_at": expires_at.isoformat(),
        "ttl_seconds": SESSION_TTL_SECONDS,
    }


@app.get("/session/dashboard")
def session_dashboard(session_id: str):
    customer_id = get_customer_id_from_session(session_id)

    if customer_id is None:
        raise HTTPException(
            status_code=401,
            detail="Sessionen er ikke gyldig. Log ind igen.",
        )

    try:
        return get_customer_dashboard(customer_id)
    except Exception as e:
        logger.exception("Fejl ved hentning af session-dashboard")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/chat-history")
def session_chat_history(session_id: str):
    customer_id = get_customer_id_from_session(session_id)

    if customer_id is None:
        raise HTTPException(
            status_code=401,
            detail="Sessionen er ikke gyldig. Log ind igen.",
        )

    return {"messages": get_saved_chat_history(customer_id)}


@app.post("/chat")
def chat(msg: Message, request: Request):
    user_text = msg.message.strip()

    if not user_text:
        raise HTTPException(status_code=400, detail="Beskeden er tom.")

    rate_limit_identifier = msg.session_id or request.client.host
    check_rate_limit(rate_limit_identifier)

    request_id = secrets.token_hex(8)

    try:
        logger.info("[%s] Chat request received", request_id)

        conversation_history = "\n".join(
            f"{m.role}: {m.content}" for m in msg.history[-6:]
        )

        customer_id = get_customer_id_from_session(msg.session_id)

        if is_closing_message(user_text):
            reply = "Selv tak. Er der andet, jeg kan hjælpe med?"

            if customer_id is not None:
                append_saved_chat_message(customer_id, "user", user_text)
                append_saved_chat_message(customer_id, "assistant", reply)

            return {
                "reply": reply,
                "sources": [],
                "provider": None,
                "fallback_used": False,
            }

        requires_customer_context = (
            not is_general_death_or_beneficiary_question(user_text)
            and (
                needs_customer_data(user_text)
                or requires_personal_assessment(user_text)
            )
        )

        if requires_customer_context and customer_id is None:
            return {
                "reply": "Du skal være logget ind for at få svar på personlige spørgsmål om din pension.",
                "sources": [],
                "provider": None,
                "fallback_used": False,
            }

        if is_obviously_out_of_scope(user_text):
            return {
                "reply": "Det fremgår ikke af mit datagrundlag.",
                "sources": [],
                "provider": None,
                "fallback_used": False,
            }

        question_type = classify_question(user_text)

        logger.info(
            "[%s] Question classified as %s",
            request_id,
            question_type,
        )

        customer_context = ""
        if requires_customer_context and customer_id is not None:
            customer_context = get_customer_context(customer_id)

        retrieval_query = f"""
Tidligere samtale:
{conversation_history}

Kundedata:
{customer_context}

Nyeste spørgsmål:
{user_text}
"""

        if question_type == "simple":
            top_k = 3
        elif question_type == "semi":
            top_k = 5
        else:
            top_k = 7
        top_chunks = retrieve_top_chunks(retrieval_query, top_k=top_k)

        if not top_chunks:
            if requires_customer_context and customer_context:
                context = "Ingen relevant generel pensionsviden fundet i RAG-konteksten. Brug kun KUNDEDATA og giv et forsigtigt vejledende svar."
                sources = []
            else:
                return {
                    "reply": "Det fremgår ikke af mit datagrundlag.",
                    "sources": [],
                    "provider": None,
                    "fallback_used": False,
                }
        else:
            context = build_context(top_chunks)
            sources = [
                {
                    "document_title": chunk["document_title"],
                    "filename": chunk["filename"],
                    "chunk_id": chunk["chunk_id"],
                }
                for chunk in top_chunks
            ]

        logger.info(
            "[%s] Retrieved %s source chunks",
            request_id,
            len(sources),
        )

        if question_type == "complex":
            extra_instruction = """
Ved komplekse personlige spørgsmål:

1. Start med en tydelig rådgivervurdering.

Første 2-3 sætninger skal direkte besvare spørgsmålet.

2. Brug kundens konkrete tal.

3. Forklar vigtigste konsekvenser.

4. Giv en vejledende rådgiveranalyse.

5. Giv 2-3 næste skridt.

Undgå generelle pensionsartikler.
Undgå FAQ-stil.
            
Spørgsmålet kræver personlig vurdering.

FORMATERING ER VIGTIG.

Brug altid tydelig struktur.

Brug typisk:

Kort indledning.

Overskrift: vigtigste forhold

Overskrift: økonomiske konsekvenser

Overskrift: forhold der bør overvejes

Overskrift: næste skridt

Brug gerne bullets ved:
- konsekvenser
- fordele
- ulemper
- forhold kunden bør overveje

Undgå lange tekstblokke.

Hvis KUNDEDATA findes:

- start med de vigtigste forhold
- brug konkrete tal
- forklar hvad tallene betyder
- sammenlign nuværende situation og alternativ
- nævn både muligheder og risici
- giv 2-3 konkrete næste skridt

Afslut med kort forbehold.

Svar skal ligne et svar fra en erfaren pensionsrådgiver — ikke en chatbot.
"""
        elif question_type == "semi":
            extra_instruction = """
Spørgsmålet handler om en situation eller livsbegivenhed.

Giv:
- kort forklaring af hvad situationen betyder
- relevante trin, hvis de fremgår af konteksten
- brug kundedata, hvis de er tilgængelige og relevante
- ét tydeligt forbehold

Hvis spørgsmålet handler om sygdom, dækning eller forsikring, så nævn relevante dækninger fra KUNDEDATA, hvis de findes.
"""
        else:
            extra_instruction = """
Spørgsmålet er simpelt.
Giv kort og direkte svar.
"""

        prompt = f"""
{SYSTEM_PROMPT}

Ekstra instruktion:
{extra_instruction}

GENEREL PENSIONSVIDEN:
{context}

KUNDEDATA:
{customer_context if customer_context else "Ingen kundedata tilgængelige."}

SAMTALEHISTORIK:
{conversation_history}

BRUGERENS SPØRGSMÅL:
{user_text}
"""

        llm_result = generate_llm_response(
            prompt,
            force_fail=msg.force_llm_fail,
        )

        if llm_result["fallback_used"]:
            logger.warning(
                "[%s] Fallback LLM provider used. Active provider: %s",
                request_id,
                llm_result["provider"],
            )

        reply = llm_result["reply"]

        if customer_id is not None:
            append_saved_chat_message(customer_id, "user", user_text)
            append_saved_chat_message(customer_id, "assistant", reply)

        return {
            "reply": reply,
            "sources": sources,
            "provider": llm_result["provider"],
            "fallback_used": llm_result["fallback_used"],
        }

    except Exception as e:
        logger.exception("[%s] Unexpected error in chat endpoint", request_id)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/debug/chat-history")
def debug_chat_history():
    cleanup_chat_history()

    return {
        "note": "Kun til lokal debugging. Chathistorik ligger kun i backend-memory og forsvinder ved restart/reload.",
        "count": len(CHAT_HISTORY_STORE),
        "history": {
            str(customer_id): {
                "expires_at": history["expires_at"].isoformat(),
                "messages": history["messages"],
            }
            for customer_id, history in CHAT_HISTORY_STORE.items()
        },
    }
