import os

from dotenv import load_dotenv
from google import genai
from mistralai import Mistral

load_dotenv()

GEMINI_MODEL = "gemini-2.5-flash"
MISTRAL_MODEL = "mistral-small-latest"

gemini_key = os.getenv("GEMINI_API_KEY")
mistral_key = os.getenv("MISTRAL_API_KEY")

if not gemini_key:
    raise RuntimeError("GEMINI_API_KEY mangler i .env")

if not mistral_key:
    raise RuntimeError("MISTRAL_API_KEY mangler i .env")

gemini_client = genai.Client(api_key=gemini_key)
mistral_client = Mistral(api_key=mistral_key)


def generate_with_gemini(prompt: str, force_fail: bool = False) -> str:
    if force_fail:
        raise RuntimeError("Simuleret Gemini LLM-fejl")

    try:
        response = gemini_client.models.generate_content(
            model=GEMINI_MODEL,
            contents=prompt,
        )

        if not response or not response.text:
            raise RuntimeError("Tomt svar fra Gemini")

        return response.text

    except Exception as e:
        print("Gemini fejlede:", type(e), repr(e))
        raise


def generate_with_mistral(prompt: str) -> str:
    try:
        response = mistral_client.chat.complete(
            model=MISTRAL_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )

        answer = response.choices[0].message.content

        if not answer:
            raise RuntimeError("Mistral returnerede tomt svar")

        return answer

    except Exception as e:
        print("Mistral fejlede:", type(e), repr(e))
        raise


def generate_llm_response(prompt: str, force_fail: bool = False) -> dict:
    print("Kalder LLM-wrapper")

    try:
        reply = generate_with_gemini(prompt, force_fail=force_fail)

        return {
            "reply": reply,
            "provider": "gemini",
            "fallback_used": False,
        }

    except Exception as gemini_error:
        print("Gemini kunne ikke bruges. Prøver Mistral:", repr(gemini_error))

        try:
            reply = generate_with_mistral(prompt)

            return {
                "reply": reply,
                "provider": "mistral",
                "fallback_used": True,
            }

        except Exception as mistral_error:
            print("Mistral kunne heller ikke bruges:", repr(mistral_error))

            return {
                "reply": (
                    "Jeg kan desværre ikke generere et svar lige nu, "
                    "fordi AI-tjenesten ikke svarer. Prøv igen om lidt."
                ),
                "provider": None,
                "fallback_used": True,
            }

