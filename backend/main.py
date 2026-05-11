import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
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

    # Kun til test af fallback. Frontend behøver ikke sende den.
    force_llm_fail: bool = False


class MitidLoginRequest(BaseModel):
    user_id: str


class LogoutRequest(BaseModel):
    session_id: str


SESSION_TTL_SECONDS = 75 * 60
CHAT_HISTORY_TTL_SECONDS = 30 * 60
SESSION_STORE: dict[str, dict[str, object]] = {}
CHAT_HISTORY_STORE: dict[int, dict[str, object]] = {}


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
            "expires_at": datetime.now(timezone.utc) + timedelta(seconds=CHAT_HISTORY_TTL_SECONDS),
        },
    )
    messages = history["messages"]
    messages.append({"role": role, "content": content})
    history["messages"] = messages[-24:]
    history["expires_at"] = datetime.now(timezone.utc) + timedelta(seconds=CHAT_HISTORY_TTL_SECONDS)


def classify_question(user_text: str) -> str:
    text = user_text.lower()

    if any(x in text for x in [
        "bør jeg",
        "skal jeg",
        "hvad er bedst",
        "hvad passer bedst",
        "gå tidligere på pension",
        "tidligere på pension",
        "for mig",
        "min situation",
        "min opsparing er",
        "mit afkast",
        "har jeg ret til",
        "må jeg",
        "kan det betale sig",
        "anbefaler du",
        "hvad vil du anbefale",
        "hvornår kan jeg gå på pension",
    ]):
        return "complex"

    if any(x in text for x in [
        "samle",
        "udbetaling",
        "begunstiget",
        "hvad gør jeg",
        "hvad skal jeg gøre",
        "jeg er blevet",
        "jeg har fået",
        "jeg mister",
        "jeg er syg",
        "skifter job",
        "nyt job",
    ]):
        return "semi"

    return "simple"


def needs_customer_data(user_text: str) -> bool:
    text = user_text.lower()

    personal_keywords = [
        "mit afkast",
        "mine forsikringer",
        "hvor meget har jeg",
        "hvad har jeg stående",
        "hvad er min månedlige indbetaling",
        "min månedlige indbetaling",
        "mine månedlige indbetalinger",
        "hvad indbetaler jeg",
        "hvor meget indbetaler jeg",
        "hvor meget betaler jeg",
        "min indbetaling",
        "mine indbetalinger",
        "min pensionsopsparing",
        "min opsparing",
        "min risikoprofil",
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
    ]

    return any(keyword in text for keyword in personal_keywords)


def is_closing_message(user_text: str) -> bool:
    text = " ".join(user_text.lower().strip().split())
    text = text.strip(".,!?:;")

    closing_messages = {
        "tak",
        "tak for hjælpen",
        "mange tak",
        "super tak",
        "tusind tak",
        "det var alt",
        "det var det",
        "nej tak",
        "ellers tak",
        "ikke mere",
        "ikke lige nu",
    }

    return text in closing_messages


SYSTEM_PROMPT = """
Du er en AI-assistent i et bachelorprojekt om pensionsrådgivning.

Du må kun svare ud fra den kontekst, du får udleveret.
Hvis svaret ikke fremgår af konteksten, skal du sige:
"Det fremgår ikke af mit datagrundlag."

Du må ikke gætte eller bruge viden uden for konteksten.
Svar kort, tydeligt og på dansk.

Du håndterer kun first-level spørgsmål, dvs. generelle og standardiserede spørgsmål om pension.
Du må ikke give personlig økonomisk, juridisk eller skattemæssig rådgivning.

Hvis der er kundedata i prompten, må du bruge dem til at forklare kundens overblik og konkrete tal.
Du må ikke opfinde kundedata, der ikke står i KUNDEDATA.

Hvis et spørgsmål kræver personlig vurdering:
- giv et kort generelt svar
- skriv tydeligt at det afhænger af brugerens situation
- anbefal kontakt til rådgiver

Ved definitionsspørgsmål:
- svar neutralt
- undgå "hos os" eller "PenSam"

Ved handlinger, fx sygdom, samle pension eller kontakt:
- du må skrive "hos PenSam" og "kontakt os"

Skriv i almindelig tekst. Ingen markdown.
"""


@app.get("/")
def root():
    return {"status": "Backend kører"}


@app.post("/mitid/resolve-user")
def resolve_mitid_user(request: MitidLoginRequest):
    try:
        customer = get_customer_by_mitid_user_id(request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Fejl ved MitID-opslag:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))

    if customer is None:
        raise HTTPException(status_code=404, detail="Bruger-ID blev ikke fundet i demo-databasen.")

    return {"customer": customer}


@app.post("/mitid/complete-login")
def complete_mitid_login(request: MitidLoginRequest):
    try:
        customer = get_customer_by_mitid_user_id(request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        print("Fejl ved MitID-login:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))

    if customer is None:
        raise HTTPException(status_code=404, detail="Bruger-ID blev ikke fundet i demo-databasen.")

    session_id = create_demo_session(customer["customer_id"])
    expires_at = get_session_payload(session_id)["expires_at"]
    return {
        "session_id": session_id,
        "expires_at": expires_at.isoformat(),
        "ttl_seconds": SESSION_TTL_SECONDS,
        "customer": customer,
    }


@app.post("/logout")
def logout(request: LogoutRequest):
    SESSION_STORE.pop(request.session_id, None)
    return {"logged_out": True}


@app.post("/session/refresh")
def refresh_login_session(request: LogoutRequest):
    expires_at = refresh_session(request.session_id)
    if expires_at is None:
        raise HTTPException(status_code=401, detail="Sessionen er ikke gyldig. Log ind igen.")

    return {
        "expires_at": expires_at.isoformat(),
        "ttl_seconds": SESSION_TTL_SECONDS,
    }


@app.post("/mitid/validate-user-id")
def validate_mitid_user(request: MitidLoginRequest):
    try:
        validate_mitid_user_id(request.user_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {"valid": True}


@app.get("/session/dashboard")
def session_dashboard(session_id: str):
    customer_id = get_customer_id_from_session(session_id)
    if customer_id is None:
        raise HTTPException(status_code=401, detail="Sessionen er ikke gyldig. Log ind igen.")

    try:
        return get_customer_dashboard(customer_id)
    except Exception as e:
        print("Fejl ved hentning af session-dashboard:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/chat-history")
def session_chat_history(session_id: str):
    customer_id = get_customer_id_from_session(session_id)
    if customer_id is None:
        raise HTTPException(status_code=401, detail="Sessionen er ikke gyldig. Log ind igen.")

    return {"messages": get_saved_chat_history(customer_id)}


@app.post("/chat")
def chat(msg: Message):
    user_text = msg.message.strip()

    if not user_text:
        raise HTTPException(status_code=400, detail="Beskeden er tom.")

    try:
        print("User text:", user_text)

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

        question_type = classify_question(user_text)
        print("Question type:", question_type)

        requires_customer_context = question_type == "complex" or needs_customer_data(user_text)

        if requires_customer_context and customer_id is None:
            return {
                "reply": "Du skal være logget ind for at få svar på personlige spørgsmål om din pension.",
                "sources": [],
                "provider": None,
                "fallback_used": False,
            }

        customer_context = ""
        if requires_customer_context and customer_id is not None:
            customer_context = get_customer_context(customer_id)

        retrieval_query = f"""
Tidligere samtale:
{conversation_history}

Nyeste spørgsmål:
{user_text}
"""

        if question_type == "simple":
            top_k = 3
        else:
            top_k = 5

        top_chunks = retrieve_top_chunks(retrieval_query, top_k=top_k)

        if not top_chunks:
            if requires_customer_context and customer_context:
                context = "Ingen relevant generel pensionsviden fundet i RAG-konteksten."
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

        print("----- CONTEXT -----")
        print(context)
        print("-------------------")

        if question_type == "complex":
            extra_instruction = """
Spørgsmålet kræver en personlig eller kompleks vurdering.
Brug kundedata forsigtigt, hvis de er tilgængelige.
Giv kun et vejledende svar.
Giv ikke endelig økonomisk, juridisk eller skattemæssig rådgivning.
Anbefal kontakt til en rådgiver ved vigtige valg eller tvivl.
"""
        elif question_type == "semi":
            extra_instruction = """
Spørgsmålet handler om en situation.
Giv:
- kort forklaring
- evt. trin hvis i kontekst
- ét forbehold
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
        print("Fejl:", repr(e))
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
