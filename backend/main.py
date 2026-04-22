import os

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai

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


class Message(BaseModel):
    message: str


SYSTEM_PROMPT = """
Du er en pensionsassistent.

Du må kun svare ud fra den kontekst, du får udleveret.
Hvis svaret ikke fremgår af konteksten, skal du sige:
"Jeg kan ikke finde tilstrækkelig information i det tilgængelige materiale."

Du må ikke gætte eller bruge viden uden for konteksten.
Svar kort, tydeligt og på dansk.
Hvis spørgsmålet kræver personlig rådgivning eller konkrete vurderinger, skal du tage forbehold og anbefale kontakt til en rådgiver.
"""


@app.post("/chat")
def chat(msg: Message):
    user_text = msg.message.strip()

    if not user_text:
        raise HTTPException(status_code=400, detail="Beskeden er tom.")

    try:
        top_chunks = retrieve_top_chunks(user_text, top_k=3)
        context = build_context(top_chunks)

        prompt = f"""
{SYSTEM_PROMPT}

Kontekst:
{context}

Brugerens spørgsmål:
{user_text}
"""

        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=prompt,
        )

        reply = response.text if response.text else "Jeg kunne ikke generere et svar."

        sources = [
            {
                "title": chunk["title"],
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
        raise HTTPException(status_code=500, detail=f"Fejl i RAG-flow: {str(e)}")