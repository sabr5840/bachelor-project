import requests
import time

BASE_URL = "http://127.0.0.1:8000"
CHAT_URL = f"{BASE_URL}/chat"
LOGIN_URL = f"{BASE_URL}/mitid/complete-login"

DEMO_USER_ID = "mette-demo"


def login() -> str:
    response = requests.post(
        LOGIN_URL,
        json={"user_id": DEMO_USER_ID},
        timeout=30,
    )

    data = response.json()

    assert response.status_code == 200
    assert "session_id" in data

    return data["session_id"]


def call_chat(
    question: str,
    force_llm_fail: bool = False,
    session_id: str | None = None,
    history=None,
) -> tuple[int, dict]:
    payload = {
        "message": question,
        "history": history or [],
        "force_llm_fail": force_llm_fail,
    }

    if session_id is not None:
        payload["session_id"] = session_id

    response = requests.post(
        CHAT_URL,
        json=payload,
        timeout=120,
    )

    # Pause så backendens rate limiter ikke blokerer testene
    time.sleep(1.2)

    try:
        data = response.json()
    except Exception:
        data = {"raw": response.text}

    return response.status_code, data