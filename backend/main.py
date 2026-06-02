import os
import logging
import re
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
    if (
        os.getenv("DISABLE_RATE_LIMIT") == "true"
        or os.getenv("TESTING") == "true"
    ):
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


def save_chat_exchange(customer_id: int | None, user_text: str, reply: str) -> None:
    if customer_id is None:
        return

    append_saved_chat_message(customer_id, "user", user_text)
    append_saved_chat_message(customer_id, "assistant", reply)


def remove_repeated_greeting(reply: str, conversation_intent: str) -> str:
    if conversation_intent == "greeting":
        return reply

    return re.sub(
        r"^\s*(hej|hejsa|kære)\s+[^,\n.!?]+[,!.]?\s*\n+",
        "",
        reply,
        count=1,
        flags=re.IGNORECASE,
    ).strip()


def soften_tax_advice_language(reply: str) -> str:
    replacements = {
        "Du bør prioritere at udnytte": "Det kan være relevant at undersøge",
        "du bør prioritere at udnytte": "det kan være relevant at undersøge",
        "Du bør udnytte": "Det kan være relevant at undersøge",
        "du bør udnytte": "det kan være relevant at undersøge",
        "Du skal udnytte": "Det kan være relevant at undersøge",
        "du skal udnytte": "det kan være relevant at undersøge",
    }

    softened = reply
    for original, replacement in replacements.items():
        softened = softened.replace(original, replacement)

    return softened


def soften_personal_recommendation_language(reply: str) -> str:
    replacements = {
        "Jeg ville især overveje": "Det kan være relevant at overveje",
        "jeg ville især overveje": "det kan være relevant at overveje",
        "Jeg ville anbefale at": "Det kan være relevant at undersøge, om du skal",
        "jeg ville anbefale at": "det kan være relevant at undersøge, om du skal",
        "Jeg ville anbefale": "Det kan være relevant at undersøge",
        "jeg ville anbefale": "det kan være relevant at undersøge",
        "Jeg anbefaler at": "Det kan være relevant at undersøge, om du skal",
        "jeg anbefaler at": "det kan være relevant at undersøge, om du skal",
        "Jeg anbefaler": "Det kan være relevant at undersøge",
        "jeg anbefaler": "det kan være relevant at undersøge",
        "Du bør samle": "Det kan være relevant at undersøge, om du skal samle",
        "du bør samle": "det kan være relevant at undersøge, om du skal samle",
        "Du bør flytte": "Det kan være relevant at undersøge, om du skal flytte",
        "du bør flytte": "det kan være relevant at undersøge, om du skal flytte",
    }

    softened = reply
    for original, replacement in replacements.items():
        softened = softened.replace(original, replacement)

    return softened


def move_inline_followup_to_suggestions(
    reply: str,
    suggestions: list[dict[str, str]],
) -> tuple[str, list[dict[str, str]]]:
    lines = [line.rstrip() for line in reply.strip().splitlines()]
    updated_suggestions = list(suggestions)
    extracted_questions: list[str] = []

    def clean_suggestion_line(line: str) -> str:
        cleaned = line.strip()
        cleaned = re.sub(r"^[-*\d.)\s]+", "", cleaned)
        cleaned = re.sub(r"^\[|\]$", "", cleaned)
        cleaned = re.sub(r"^#+\s*", "", cleaned)
        cleaned = re.sub(r"<[^>]+>", "", cleaned)
        return cleaned.strip(" \"'")

    def is_suggestion_line(line: str) -> bool:
        cleaned = clean_suggestion_line(line)
        lower = cleaned.lower()

        return (
            0 < len(cleaned) <= 140
            and (
                cleaned.endswith("?")
                or lower.startswith("fortæl mig")
                or lower.startswith("spørg")
                or lower.startswith("skriv")
                or lower.startswith("hvis du vil vide mere")
                or lower.startswith("har du spørgsmål")
            )
        )

    while lines and not lines[-1].strip():
        lines.pop()

    while lines and is_suggestion_line(lines[-1]):
        extracted = clean_suggestion_line(lines.pop())

        if extracted.lower().startswith("har du spørgsmål"):
            continue

        extracted_questions.insert(0, extracted)

        while lines and not lines[-1].strip():
            lines.pop()

    if not extracted_questions:
        return reply, suggestions

    existing_messages = {
        suggestion.get("message")
        for suggestion in updated_suggestions
        if suggestion.get("message")
    }

    new_suggestions = []
    for question in extracted_questions:
        if question in existing_messages:
            continue

        new_suggestions.append(
            {
                "label": question,
                "message": question,
            },
        )
        existing_messages.add(question)

    updated_suggestions = new_suggestions + updated_suggestions

    cleaned_reply = "\n".join(lines).strip()
    return cleaned_reply or reply, updated_suggestions


def remove_disallowed_chat_sections(reply: str) -> str:
    lines = reply.strip().splitlines()
    cleaned_lines = []

    for line in lines:
        stripped = line.strip()
        normalized = stripped.lower().strip("*:# ")

        if normalized in {"næste skridt", "næste skridt:"}:
            break

        if normalized.startswith("næste skridt"):
            break

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def limit_reply_length(reply: str, max_words: int = 85) -> str:
    paragraphs = [paragraph.strip() for paragraph in reply.split("\n\n") if paragraph.strip()]
    if len(paragraphs) > 2:
        reply = "\n\n".join(paragraphs[:2])

    lines = reply.splitlines()
    bullet_count = 0
    kept_lines = []

    for line in lines:
        if line.strip().startswith(("-", "*", "•")):
            bullet_count += 1
            if bullet_count > 2:
                continue

        kept_lines.append(line)

    reply = "\n".join(kept_lines).strip()
    words = reply.split()

    if len(words) <= max_words:
        return reply

    shortened = " ".join(words[:max_words]).rstrip(" ,;:")
    sentence_end = max(shortened.rfind("."), shortened.rfind("?"), shortened.rfind("!"))

    if sentence_end > 40:
        return shortened[: sentence_end + 1]

    return f"{shortened}."


# ============================================================
# QUESTION CLASSIFICATION
# ============================================================


def normalize_chat_text(user_text: str) -> str:
    return " ".join(user_text.lower().strip(" !?.").split())


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

    if is_general_death_or_beneficiary_question(user_text):
        return False

    scenario_exceptions = [
        "hvordan vokser min pensionsopsparing over tid",
        "hvordan vokser min opsparing over tid",
    ]

    if any(x in text for x in scenario_exceptions):
        return False

    personal_keywords = [
        "mit afkast",
        "min begunstigelse",
        "min begunstiget",
        "min begunstigede",
        "hvem er min begunstigede",
        "hvem er begunstiget",
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


def is_greeting_message(user_text: str) -> bool:
    normalized = normalize_chat_text(user_text)

    greeting_messages = {
        "hej",
        "hejsa",
        "hej med dig",
        "godmorgen",
        "god formiddag",
        "god eftermiddag",
        "godaften",
        "halløj",
        "hello",
        "hi",
    }

    return normalized in greeting_messages



def is_broad_personal_overview_question(user_text: str) -> bool:
    text = normalize_chat_text(user_text)

    broad_patterns = [
        "hvordan ser min pension ud",
        "giv mig et overblik",
        "kan du give mig et overblik",
        "overblik over min pension",
        "mit pensionsoverblik",
        "vis mig min pension",
        "fortæl om min pension",
        "hvordan står jeg",
        "hvordan går det med min pension",
        "status på min pension",
    ]

    return any(pattern in text for pattern in broad_patterns)


def is_life_event_question(user_text: str) -> bool:
    text = user_text.lower()

    life_event_keywords = [
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
        "jeg er syg",
        "alvorligt syg",
        "kritisk sygdom",
        "tab af erhvervsevne",
        "død",
        "doed",
        "afdød",
        "afdoed",
    ]

    return any(keyword in text for keyword in life_event_keywords)


def classify_conversation_intent(user_text: str) -> str:
    if is_greeting_message(user_text):
        return "greeting"

    if is_closing_message(user_text):
        return "closing"

    if is_broad_personal_overview_question(user_text):
        return "personal_overview"

    if requires_personal_assessment(user_text):
        return "personal_decision"

    if is_life_event_question(user_text):
        return "life_event"

    if needs_customer_data(user_text):
        return "personal_info"

    if is_obviously_out_of_scope(user_text):
        return "out_of_scope"

    return "general_info"


def get_greeting_reply(customer_id: int | None) -> str:
    if customer_id is not None:
        return (
            "Hej. Jeg kan hjælpe med at forklare dine pensionstal eller svare "
            "på generelle pensionsspørgsmål. Hvad vil du gerne se på?"
        )

    return (
        "Hej. Jeg kan hjælpe med generelle spørgsmål om pension. Hvis du spørger "
        "om dine egne tal, skal du være logget ind."
    )


def get_personal_overview_choice_reply() -> str:
    return (
        "Jeg kan give dig et kort overblik over din pension. Hvad vil du helst "
        "starte med?\n\n"
        "- Opsparing og indbetaling\n"
        "- Forventet udbetaling\n"
        "- Forsikringer og dækninger\n"
        "- Risiko og investering"
    )


def get_login_required_reply(conversation_intent: str) -> str:
    if conversation_intent == "personal_overview":
        return (
            "Det kræver, at du er logget ind, så jeg kan se dine pensionsoplysninger. Log ind, "
            "så kan jeg hjælpe dig med overblik over opsparing, udbetaling, "
            "forsikringer eller risiko."
        )

    return (
        "Det kræver, at du er logget ind, så jeg kan se dine pensionsoplysninger. Log ind, "
        "så kan jeg forklare dine tal."
    )


def get_flow_instruction(conversation_intent: str, customer_id: int | None) -> str:
    logged_in = customer_id is not None

    if conversation_intent == "general_info":
        return (
            "Svar kort: forklaring først, derefter eventuelt én relevant opfølgning. "
            "Afslut gerne med at kunden kan læse mere på hjemmesiden eller spørge her."
        )

    if conversation_intent == "personal_info":
        return (
            "Svar med kundens konkrete data først. Forklar kort hvad tallet betyder. "
            "Skriv ikke opfølgende spørgsmål i selve svaret, da de vises som klikbare "
            "knapper under svaret. Nævn ikke login, når kunden er logget ind."
            if logged_in
            else "Bed kunden logge ind for personlige tal."
        )

    if conversation_intent == "personal_decision":
        return (
            "Svar i et meget kort chatformat: 1 sætning med kundens relevante tal, "
            "og 1 sætning med vurderingen. Skriv ikke opfølgende spørgsmål i selve svaret, "
            "da de vises som klikbare knapper under svaret. "
            "Brug markdown. Markér de vigtigste tal med fed, fx **6.200 kr.** og **28.000 kr.**. "
            "Medtag kun tal, der direkte besvarer spørgsmålet. Undlad årsindkomst, "
            "alder og ekstra forklaringer, medmindre kunden spørger om det. "
            "Beslut ikke for kunden. Skriv ikke hilsen eller kundens navn. Nævn ikke "
            "login, når kunden er logget ind. Hold svaret under cirka 65 ord."
            if logged_in
            else "Bed kunden logge ind for personlig vurdering."
        )

    if conversation_intent == "life_event":
        return (
            "Forklar kort hvad situationen typisk betyder, nævn kundedata hvis relevant, "
            "og hold svaret kort. Skriv ikke 'Næste skridt'. Eventuelle opfølgninger "
            "vises som klikbare knapper."
        )

    if conversation_intent == "personal_overview":
        return (
            "Brug ikke en lang rapport. Hvis spørgsmålet er bredt, hjælp kunden med at "
            "vælge næste fokusområde: opsparing, udbetaling, forsikringer eller risiko."
        )

    return "Svar kort. Skriv ikke opfølgende spørgsmål i selve svaret, da forslag vises som klikbare knapper."


def build_suggestion(label: str, message: str | None = None) -> dict[str, str]:
    return {
        "label": label,
        "message": message or label,
    }


def filter_chat_suggestions(
    suggestions: list[dict[str, str]],
    user_text: str,
    max_count: int = 3,
) -> list[dict[str, str]]:
    normalized_user_text = normalize_chat_text(user_text)
    seen = set()
    filtered = []

    for suggestion in suggestions:
        label = suggestion.get("label", "")
        message = suggestion.get("message", label)
        normalized_message = normalize_chat_text(message)

        if not label or normalized_message in seen:
            continue

        if normalized_message == normalized_user_text:
            continue

        seen.add(normalized_message)
        filtered.append(suggestion)

        if len(filtered) >= max_count:
            break

    return filtered


def get_chat_suggestions(conversation_intent: str, user_text: str, customer_id: int | None) -> list[dict[str, str]]:
    if conversation_intent == "personal_decision" and customer_id is not None:
        text = user_text.lower()

        if "indbetal" in text:
            suggestions = [
                build_suggestion("Hvordan fordeler jeg mine indbetalinger?"),
                build_suggestion("Hvad betyder det for min udbetaling?"),
            ]
        elif "risiko" in text or "invest" in text:
            suggestions = [
                build_suggestion("Hvad betyder min risikoprofil?"),
                build_suggestion("Hvordan er min pension investeret?"),
            ]
        elif "udbetal" in text or "pensionist" in text:
            suggestions = [
                build_suggestion("Hvad betyder udbetalingsperioden for mig?"),
                build_suggestion("Hvad får jeg udbetalt om måneden?"),
            ]
        else:
            suggestions = [
                build_suggestion("Hvad bør jeg være mest opmærksom på?"),
                build_suggestion("Hvad betyder det for min pension?"),
            ]

        suggestions.append({"label": "Kontakt rådgiver", "action": "contact_advisor"})
        return filter_chat_suggestions(suggestions, user_text)

    if conversation_intent == "personal_info" and customer_id is not None:
        text = user_text.lower()

        if "invest" in text or "risiko" in text or "aktier" in text:
            suggestions = [
                build_suggestion("Hvad betyder min risikoprofil?"),
                build_suggestion("Bør jeg ændre min risikoprofil?"),
                build_suggestion("Hvad betyder investeringerne for min pension?"),
            ]
        elif "indbetal" in text or "betaler jeg" in text:
            suggestions = [
                build_suggestion("Hvordan fordeler jeg mine indbetalinger?"),
                build_suggestion("Bør jeg indbetale mere?"),
                build_suggestion("Hvad betyder det for min udbetaling?"),
            ]
        elif "udbetal" in text or "pensionist" in text:
            suggestions = [
                build_suggestion("Hvad betyder udbetalingsperioden for mig?"),
                build_suggestion("Kan jeg gå tidligere på pension?"),
                build_suggestion("Hvad påvirker min udbetaling?"),
            ]
        elif "forsikring" in text or "dækning" in text or "dækninger" in text:
            suggestions = [
                build_suggestion("Hvad dækker mine forsikringer?"),
                build_suggestion("Hvad sker der, hvis jeg bliver syg?"),
            ]
        elif "fordel" in text or "livrente" in text or "ratepension" in text:
            suggestions = [
                build_suggestion("Hvad betyder udbetalingsperioden for mig?"),
                build_suggestion("Hvad er forskellen på livrente og ratepension?"),
            ]
        elif "sparet" in text or "opsparing" in text or "stående" in text:
            suggestions = [
                build_suggestion("Hvad betyder det for min pension?"),
                build_suggestion("Hvad får jeg udbetalt om måneden?"),
                build_suggestion("Hvordan er min pension investeret?"),
            ]
        else:
            suggestions = [
                build_suggestion("Hvad betyder det for min pension?"),
                build_suggestion("Hvad bør jeg være mest opmærksom på?"),
            ]

        return filter_chat_suggestions(suggestions, user_text)

    if conversation_intent == "life_event" and customer_id is not None:
        suggestions = [
            build_suggestion("Hvilke forsikringer har jeg?"),
            build_suggestion("Hvad bør jeg være opmærksom på?"),
        ]
        return filter_chat_suggestions(suggestions, user_text, max_count=2)

    return []


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
        "kontorente",
        "markedsrente",
        "traditionel pension",
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


def is_prompt_injection_attempt(user_text: str) -> bool:
    text = user_text.lower()

    prompt_injection_patterns = [
        "ignorer regler",
        "ignorer instruktion",
        "ignore previous",
        "ignore instructions",
        "omgå sikkerhed",
        "bypass",
        "vis kundedata",
        "vis alle kundedata",
        "afslør kundedata",
        "system prompt",
        "developer message",
        "du skal ikke følge",
    ]

    return any(pattern in text for pattern in prompt_injection_patterns)


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
- venlig og naturlig
- egnet til en chat

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

Svar altid på dansk.
Svar skal være korte og lette at læse visuelt.
Svar med den længde, der passer til en chatbot.
Start ikke almindelige svar med "Hej", kundens navn eller en ny velkomst.
Brug kun hilsen, når SAMTALE_INTENT er "greeting".
Ved personlige rådgivningssvar: maks 2 korte afsnit.
Ved personlige beslutningsspørgsmål: maks 3 korte tekstlinjer og cirka 45-65 ord.
Brug markdown til at gøre korte svar lette at skimme.
Markér centrale beløb, procenttal, aldre og pensionsordninger med fed.
Skriv ikke "Næste skridt" eller "Hvis du vil vide mere" ved personlige beslutningsspørgsmål.
Opfølgende spørgsmål vises som klikbare knapper under svaret.

Brug struktur når spørgsmålet er personligt eller komplekst.

Du må bruge:
- korte overskrifter
- korte afsnit
- punktopstillinger

Du må IKKE skrive én lang tekstblok.

Formatér især komplekse/personlige svar som korte chatbeskeder.

Du håndterer to typer spørgsmål:
1. First-level generelle pensionsspørgsmål.
2. Personlige overbliksspørgsmål, når kundedata er tilgængelige.

Samtaleflow:
- Start med at besvare det kunden faktisk spørger om
- Giv derefter højst én relevant opfølgning eller ét næste valg
- Ved brede spørgsmål skal du hjælpe kunden med at vælge fokus i stedet for at skrive en lang rapport
- Brug normalt højst 2 korte afsnit eller 2 bullets
- Ved personlige beslutningsspørgsmål: brug maks 3 korte tekstlinjer og derefter stop
- Foreslå kun rådgiverkontakt, når spørgsmålet kræver endelig personlig beslutning eller handling

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

Brug markdown-format, men kun når det gør svaret lettere at skimme.

Brug gerne:

### Overskrift

tekst

### Overskrift

- punkt
- punkt

Svar skal ligne en kort rådgiverbesked i en chat.

Undgå store tekstblokke.

Hold sektionerne korte og tydelige.

- brug konkrete tal fra KUNDEDATA
- skriv som en erfaren pensionsrådgiver i et rådgivningsmøde
- skriv naturligt og forklarende
- prioriter kundens vigtigste 1-3 forhold
Vælg aktivt de mest betydningsfulde observationer fra kundedata.

Ikke alle data er lige vigtige.

Spørg dig selv:

"Hvis jeg sad i et rigtigt rådgivningsmøde — hvad ville jeg være mest opmærksom på hos denne kunde?"

Prioritér derefter svaret.

- fremhæv hvad der er mest relevant i netop kundens situation
- undgå at gennemgå alle mulige pensionsemner
- undgå punkt-for-punkt rapportstil
- forklar tallene i almindeligt sprog
- prioriter de 1-3 vigtigste pointer fremfor lange lister
- vær konkret og analytisk
- undgå lange generelle forklaringer
- forklar hvad tallene betyder for kunden
- fokuser på de vigtigste konsekvenser
- skriv ikke "Næste skridt"

skriv typisk 40-90 ord.

Korte spørgsmål:
20-70 ord.

Komplekse/personlige spørgsmål:
45-80 ord.

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
Du må ikke skrive "Jeg ville anbefale", "Jeg anbefaler", "Jeg ville især overveje" eller lignende personlige anbefalingsformuleringer.
Brug i stedet "Det kan være relevant at undersøge...", "En mulighed er..." eller "Det afhænger af...".
Du må ikke skrive, at kunden "bør prioritere", "bør udnytte" eller "skal udnytte" skattefradrag, indbetalingslofter eller andre skatteforhold.
Ved skattefradrag, indbetalingslofter og PAL-skat må du kun skrive, at det kan være relevant at undersøge eller tale med en rådgiver om.
Formulér økonomiske og skattemæssige valg som muligheder og forhold, kunden skal være opmærksom på, ikke som instruktioner.

Du må gerne prioritere relevante forhold, hvis KUNDEDATA giver et rimeligt grundlag, men du må ikke formulere det som en personlig anbefaling.

Brug formuleringer som:

"Det kan være relevant at undersøge..."
"Et muligt fokusområde er..."
"Hvis målet er X, peger dine data på, at du bør undersøge..."

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
- skriv ikke at kunden bør udnytte fradrag eller indbetalingslofter
- skriv i stedet "det kan være relevant at undersøge fradrag og indbetalingslofter"

Hvis SESSION_STATUS siger, at kunden er logget ind:
- skriv ikke, at kunden skal logge ind
- skriv ikke, at kunden skal logge ind på Mit PenSam eller Mit Pensam
- svar ud fra kundedata og den generelle kontekst, der findes

Hvis SESSION_STATUS siger, at kunden ikke er logget ind, og spørgsmålet kræver kundedata:
- sig kort, at kunden skal være logget ind for personlige oplysninger

Ved generelle emner må du gerne afslutte kort med:
"Du kan også læse mere på hjemmesiden eller spørge her."
Brug kun denne afslutning, når den føles relevant, og ikke i alle svar.

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


def is_specific_investment_advice_question(user_text: str) -> bool:
    text = user_text.lower()

    blocked_patterns = [
        "bestemt aktie",
        "konkret aktie",
        "anbefale mig en aktie",
        "anbefale en aktie",
        "anbefale aktie",
        "hvilken aktie",
        "køb aktie",
        "købe aktie",
        "aktietip",
        "stock pick",
    ]

    return any(pattern in text for pattern in blocked_patterns)

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
        conversation_intent = classify_conversation_intent(user_text)

        if is_prompt_injection_attempt(user_text):
            return {
                "reply": "Jeg kan ikke vise kundedata eller omgå sikkerhedsregler.",
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        if is_specific_investment_advice_question(user_text):
            return {
                "reply": (
                    "Jeg kan ikke anbefale konkrete aktier eller individuelle investeringer. "
                    "Jeg kan hjælpe med generelle spørgsmål om pension, risiko og pensionsinvestering."
                ),
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        if conversation_intent == "greeting":
            reply = get_greeting_reply(customer_id)
            save_chat_exchange(customer_id, user_text, reply)

            return {
                "reply": reply,
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        if conversation_intent == "closing":
            reply = "Selv tak. Er der andet, jeg kan hjælpe med?"
            save_chat_exchange(customer_id, user_text, reply)

            return {
                "reply": reply,
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        if conversation_intent == "personal_overview" and customer_id is not None:
            reply = get_personal_overview_choice_reply()
            save_chat_exchange(customer_id, user_text, reply)

            return {
                "reply": reply,
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [
                    {"label": "Opsparing og indbetaling", "message": "Opsparing og indbetaling"},
                    {"label": "Forventet udbetaling", "message": "Forventet udbetaling"},
                    {"label": "Forsikringer", "message": "Forsikringer og dækninger"},
                    {"label": "Risiko", "message": "Risiko og investering"},
                ],
            }

        if conversation_intent == "personal_overview" and customer_id is None:
            reply = get_login_required_reply(conversation_intent)

            return {
                "reply": reply,
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        requires_customer_context = (
            not is_general_death_or_beneficiary_question(user_text)
            and (
                needs_customer_data(user_text)
                or requires_personal_assessment(user_text)
            )
        )

        if requires_customer_context and customer_id is None:
            reply = get_login_required_reply(conversation_intent)

            return {
                "reply": reply,
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        if conversation_intent == "out_of_scope":
            return {
                "reply": "Jeg kan kun hjælpe med spørgsmål om pension og pensionsordninger. Det fremgår derfor ikke af mit datagrundlag.",
                "sources": [],
                "provider": None,
                "fallback_used": False,
                "suggestions": [],
            }

        question_type = classify_question(user_text)
        flow_instruction = get_flow_instruction(conversation_intent, customer_id)

        logger.info(
            "[%s] Question classified as %s / %s",
            request_id,
            question_type,
            conversation_intent,
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
                context = (
                    "Ingen relevant generel pensionsviden fundet i RAG-konteksten. "
                    "Brug kun KUNDEDATA og giv et forsigtigt vejledende svar."
                )
                sources = []
            else:
                return {
                    "reply": "Det fremgår ikke af mit datagrundlag.",
                    "sources": [],
                    "provider": None,
                    "fallback_used": False,
                    "suggestions": [],
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

        logger.info("[%s] Retrieved %s source chunks", request_id, len(sources))

        if question_type == "complex":
            extra_instruction = """
Ved komplekse personlige spørgsmål:

1. Start med kun de kundetal, der direkte besvarer spørgsmålet.
Første sætning skal direkte besvare spørgsmålet.

2. Forklar kun den vigtigste betydning for kunden i én kort sætning.

3. Stop efter vurderingen. Opfølgende spørgsmål vises som klikbare knapper under svaret.

Format:
- kundetal og status
- kort vurdering

Undgå generelle pensionsartikler.
Undgå FAQ-stil.

Spørgsmålet kræver personlig vurdering, men svaret skal stadig føles som en kort chatbesked.

Brug kun bullets, hvis det gør svaret kortere.

Undgå lange tekstblokke.

Hvis KUNDEDATA findes:

- start med de vigtigste forhold
- brug kun konkrete tal der direkte besvarer spørgsmålet
- markér de vigtigste tal med fed markdown
- undlad årsindkomst, alder og andre ekstra oplysninger, medmindre kunden spørger om det
- forklar kun den vigtigste betydning
- undgå "overvej dit pensionsbudget" og andre abstrakte råd
- undgå formuleringer som "du bør prioritere", "du bør udnytte fradrag" og "du skal udnytte fradrag"
- ved fradrag og indbetalingslofter: skriv kun at kunden kan undersøge det eller tale med rådgiver

Afslut med kort forbehold.

Skriv ikke "Hej" eller kundens navn.
Skriv ikke "Næste skridt" eller "Hvis du vil vide mere" ved personlige beslutningsspørgsmål.
Svar skal være meget kort og typisk under 70 ord.
"""
        elif question_type == "semi":
            extra_instruction = """
Spørgsmålet handler om en situation eller livsbegivenhed.

Giv:
- kort forklaring af hvad situationen betyder
- relevante trin, hvis de fremgår af konteksten
- brug kundedata, hvis de er tilgængelige og relevante
- ét tydeligt forbehold
- hold svaret på cirka 60-130 ord

Hvis spørgsmålet handler om sygdom, dækning eller forsikring, så nævn relevante dækninger fra KUNDEDATA, hvis de findes.
"""
        else:
            extra_instruction = """
Spørgsmålet er simpelt.
Giv kort og direkte svar på cirka 20-80 ord.
Hvis det er et generelt emne, må du kort foreslå, at kunden kan læse mere på hjemmesiden eller spørge her.
"""

        prompt = f"""
{SYSTEM_PROMPT}

Ekstra instruktion:
{extra_instruction}

GENEREL PENSIONSVIDEN:
{context}

KUNDEDATA:
{customer_context if customer_context else "Ingen kundedata tilgængelige."}

SESSION_STATUS:
{"Kunden er logget ind." if customer_id is not None else "Kunden er ikke logget ind."}

SAMTALE_INTENT:
{conversation_intent}

SAMTALEFLOW:
{flow_instruction}

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

        reply = remove_repeated_greeting(llm_result["reply"], conversation_intent)
        reply = soften_tax_advice_language(reply)
        reply = soften_personal_recommendation_lang