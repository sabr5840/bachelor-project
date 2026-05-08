from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from customer_repository import get_customer_context
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
    customer_id: Optional[int] = None
    history: List[ChatMessage] = Field(default_factory=list)

    # Kun til test af fallback. Frontend behøver ikke sende den.
    force_llm_fail: bool = False


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
        "min pensionsopsparing",
        "min opsparing",
        "min risikoprofil",
        "min pension investeret",
        "min pension er investeret",
        "hvordan er min pension investeret",
        "mine pensionsordninger",
        "mine omkostninger",
        "min pal-skat",
        "min skattekode",
        "hvad er min skattekode",
    ]

    return any(keyword in text for keyword in personal_keywords)


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

        question_type = classify_question(user_text)
        print("Question type:", question_type)

        requires_customer_context = question_type == "complex" or needs_customer_data(user_text)

        if requires_customer_context and msg.customer_id is None:
            return {
                "reply": "Du skal være logget ind for at få svar på personlige spørgsmål om din pension.",
                "sources": [],
                "provider": None,
                "fallback_used": False,
            }

        customer_context = ""
        if requires_customer_context and msg.customer_id is not None:
            customer_context = get_customer_context(msg.customer_id)

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

        return {
            "reply": llm_result["reply"],
            "sources": sources,
            "provider": llm_result["provider"],
            "fallback_used": llm_result["fallback_used"],
        }

    except Exception as e:
        print("Fejl:", repr(e))
        raise HTTPException(status_code=500, detail=str(e))
