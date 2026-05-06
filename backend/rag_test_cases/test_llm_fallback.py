# for at køre test skriv følgende i terminalen: python3 backend/rag_test_cases/test_llm_fallback.py (husk at have backend kørende)

import requests

URL = "http://127.0.0.1:8000/chat"


def call_chat(
    question: str,
    force_llm_fail: bool = False,
    customer_id=None,
    history=None,
) -> tuple[int, dict]:
    payload = {
        "message": question,
        "history": history or [],
        "force_llm_fail": force_llm_fail,
    }

    if customer_id is not None:
        payload["customer_id"] = customer_id

    response = requests.post(
        URL,
        json=payload,
        timeout=120,
    )

    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}

    return response.status_code, data


def assert_ok_response(data: dict) -> None:
    assert "reply" in data
    assert "sources" in data
    assert "provider" in data
    assert "fallback_used" in data
    assert data["reply"]


def test_normal_gemini() -> None:
    print("\nTEST 1: Normal Gemini-kald")

    status, data = call_chat("Hvad er ratepension?")

    print(data)

    assert status == 200
    assert_ok_response(data)
    assert data["provider"] == "gemini"
    assert data["fallback_used"] is False
    assert len(data["sources"]) > 0

    print("TEST 1 bestået")


def test_mistral_fallback() -> None:
    print("\nTEST 2: Mistral fallback")

    status, data = call_chat(
        question="Hvad er ratepension?",
        force_llm_fail=True,
    )

    print(data)

    assert status == 200
    assert_ok_response(data)
    assert data["provider"] == "mistral"
    assert data["fallback_used"] is True
    assert len(data["sources"]) > 0

    print("TEST 2 bestået")


def test_empty_message() -> None:
    print("\nTEST 3: Tom besked")

    status, data = call_chat("")

    print(data)

    assert status == 400
    assert "detail" in data

    print("TEST 3 bestået")


def test_out_of_scope_question() -> None:
    print("\nTEST 4: Out-of-scope spørgsmål")

    status, data = call_chat("Hvad er moms?")

    print(data)

    assert status == 200
    assert "reply" in data
    assert data["reply"]
    assert "datagrundlag" in data["reply"].lower() or data["sources"] == []

    print("TEST 4 bestået")


def test_customer_question_without_login() -> None:
    print("\nTEST 5: Kundespecifikt spørgsmål uden login")

    status, data = call_chat("Hvor meget har jeg stående på min pension?")

    print(data)

    assert status == 200
    assert "reply" in data
    assert "logget ind" in data["reply"].lower()
    assert data["provider"] is None

    print("TEST 5 bestået")


def test_customer_question_with_customer_id() -> None:
    print("\nTEST 6: Kundespecifikt spørgsmål med customer_id")

    status, data = call_chat(
        question="Hvor meget har jeg stående på min pension?",
        customer_id=1,
    )

    print(data)

    assert status == 200
    assert "reply" in data
    assert "ikke implementeret" in data["reply"].lower() or "personlige data" in data["reply"].lower()

    print("TEST 6 bestået")


def test_with_history() -> None:
    print("\nTEST 7: Samtalehistorik")

    history = [
        {
            "role": "user",
            "content": "Hvad er ratepension?",
        },
        {
            "role": "assistant",
            "content": "Ratepension udbetales over en begrænset periode.",
        },
    ]

    status, data = call_chat(
        question="Og hvad er forskellen på livrente?",
        history=history,
    )

    print(data)

    assert status == 200
    assert_ok_response(data)
    assert data["provider"] in ["gemini", "mistral"]

    print("TEST 7 bestået")


def test_long_question() -> None:
    print("\nTEST 8: Langt spørgsmål")

    question = (
        "Jeg prøver at forstå pension bedre, fordi jeg har hørt om ratepension, "
        "livrente og aldersopsparing, men jeg er lidt forvirret over forskellen. "
        "Kan du forklare forskellen på de tre pensionstyper på en simpel måde?"
    )

    status, data = call_chat(question)

    print(data)

    assert status == 200
    assert_ok_response(data)
    assert len(data["reply"]) > 50

    print("TEST 8 bestået")


def test_multiple_requests() -> None:
    print("\nTEST 9: Flere kald i træk")

    questions = [
        "Hvad er ratepension?",
        "Hvad er livrente?",
        "Hvad er aldersopsparing?",
    ]

    for question in questions:
        status, data = call_chat(question)

        print(question)
        print(data)

        assert status == 200
        assert_ok_response(data)
        assert data["provider"] == "gemini"
        assert data["fallback_used"] is False

    print("TEST 9 bestået")


def main() -> None:
    print("\nKører udvidet LLM fallback- og grænsetest...")
    print("Backend skal køre på http://127.0.0.1:8000")

    test_normal_gemini()
    test_mistral_fallback()
    test_empty_message()
    test_out_of_scope_question()
    test_customer_question_without_login()
    test_customer_question_with_customer_id()
    test_with_history()
    test_long_question()
    test_multiple_requests()

    print("\nAlle tests gennemført korrekt.")


if __name__ == "__main__":
    main()