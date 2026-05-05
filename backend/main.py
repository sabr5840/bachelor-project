import os
from typing import List

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from google import genai
from pydantic import BaseModel, Field

from rag_pipeline import retrieve_top_chunks, build_context

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # kun til lokal udvikling
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise RuntimeError("GEMINI_API_KEY mangler i .env")

client = genai.Client(api_key=api_key)

MODEL_NAME = "gemini-2.5-flash"


class ChatMessage(BaseModel):
    role: str
    content: str


class Message(BaseModel):
    message: str
    history: List[ChatMessage] = Field(default_factory=list)


def classify_question(user_text: str) -> str:
    text = user_text.lower()

    if any(x in text for x in [
        "bør jeg",
        "skal jeg",
        "hvad er bedst",
        "kan jeg få",

        "hvad passer bedst",
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
    ]):
        return "semi"

    return "simple"


def get_fallback_reply() -> str:
    return (
        "Det spørgsmål kræver en vurdering af din konkrete situation. "
        "Jeg kan ikke give personlig rådgivning, men jeg kan godt forklare de generelle regler."
    )


SYSTEM_PROMPT = """
Du er en AI-assistent i et bachelorprojekt om pensionsrådgivning.

Du må kun svare ud fra den kontekst, du får udleveret.
Hvis svaret ikke fremgår af konteksten, skal du sige:
"Det fremgår ikke af mit datagrundlag."

Du må ikke gætte eller bruge viden uden for konteksten.
Svar kort, tydeligt og på dansk.

Du håndterer kun first-level spørgsmål, dvs. generelle og standardiserede spørgsmål om pension.
Du må ikke give personlig økonomisk, juridisk eller skattemæssig rådgivning.
Hvis et spørgsmål kræver personlig vurdering, skal du tage forbehold og anbefale kontakt til en rådgiver.

Ved generelle definitionsspørgsmål, fx "hvad er ratepension?", skal du svare neutralt og ikke skrive "hos PenSam" eller "hos os".

Hvis spørgsmålet handler om en konkret handling, service eller vejledning hos PenSam, fx at samle pension, ændre begunstigelse, finde overblik eller kontakte rådgiver, må du formulere svaret i en PenSam-kontekst.
I den situation må du skrive som PenSam, fx "hos PenSam", "hos os", "vi kan hjælpe" og "kontakt os", men kun hvis det er i overensstemmelse med den givne kontekst.

Hvis et spørgsmål kan forstås bredt, skal du starte med en generel forklaring og derefter præcisere relevante særlige tilfælde fra konteksten.

Ved hvorfor-spørgsmål skal du starte med en direkte årsagsforklaring i første sætning, før du uddyber med regler eller eksempler.

Hvis spørgsmålet er generelt, fx "kan jeg få pension udbetalt som engangsbeløb", skal du tydeligt afgrænse svaret og forklare, at det afhænger af typen af pension.
Undgå at starte med "Ja", hvis svaret ikke gælder alle tilfælde.
Brug ikke markdown-formattering. Skriv i almindelig tekst.
Hvis konteksten indeholder centrale tal som satser, perioder eller grænser, må du gerne nævne dem kort i svaret.

Du må aldrig bruge markdown. Brug ikke stjerner, punktopstillinger, fed skrift eller nummererede lister, medmindre brugeren specifikt beder om en liste.
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

        retrieval_query = f"""
Tidligere samtale:
{conversation_history}

Nyeste spørgsmål:
{user_text}
"""

        # Use fewer chunks for simple questions and more chunks for broader questions.
        if question_type == "simple":
            top_k = 3
        elif question_type == "semi":
            top_k = 3
        else:
            top_k = 5

        top_chunks = retrieve_top_chunks(retrieval_query, top_k=top_k)

        if not top_chunks:
            return {
                "reply": "Det fremgår ikke af mit datagrundlag.",
                "sources": []
            }

        context = build_context(top_chunks)

        print("----- RETRIEVED CONTEXT -----")
        print(context)
        print("-----------------------------")

        if question_type == "complex":
            extra_instruction = """
Spørgsmålet kræver en personlig vurdering.
Du skal:
- først give et kort generelt svar baseret på konteksten
- derefter tydeligt skrive, at det afhænger af brugerens situation
- anbefale kontakt til en rådgiver
- undgå at give konkret personlig rådgivning
"""
        elif question_type == "semi":
            extra_instruction = """
Spørgsmålet handler om en handling eller situation.
Du skal:
- give et kort svar på hvad situationen betyder
- hvis konteksten indeholder trin-for-trin handlinger, gengiv dem kort og konkret
- inkludere ét kort forbehold
- anbefale kontakt til en rådgiver, hvis spørgsmålet kræver personlig vurdering
- undgå lange forklaringer
- skriv i almindelig tekst uden markdown
"""
        else:
            extra_instruction = """
Spørgsmålet er et first-level spørgsmål.
Du skal give et kort, klart og direkte svar.
Brug ikke markdown, punktlister, stjerner eller overskrifter.
Skriv i almindelig tekst.
Hvis konteksten indeholder centrale tal som satser, perioder eller grænser, må du gerne nævne dem kort i svaret.
- hvis konteksten indeholder trin-for-trin handlinger, skal du gengive dem kort og konkret
"""

        prompt = f"""
{SYSTEM_PROMPT}

Ekstra instruktion:
{extra_instruction}

Kontekst:
{context}

Tidligere samtale:
{conversation_history}

Brugerens nyeste spørgsmål:
{user_text}
"""

        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=prompt,
        )

        reply = response.text if response.text else "Jeg kunne ikke generere et svar."

        sources = [
            {
                "document_title": chunk["document_title"],
                "filename": chunk["filename"],
                "chunk_id": chunk["chunk_id"],
            }
            for chunk in top_chunks
        ]

        return {
            "reply": reply,
            "sources": sources,
        }

    except Exception as e:
        print("Fejl i RAG-flow:", repr(e))
        raise HTTPException(status_code=500, detail=f"Fejl i RAG-flow: {str(e)}")