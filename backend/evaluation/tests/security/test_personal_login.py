import requests


BASE_URL = "http://127.0.0.1:8000"
LOGIN_URL = f"{BASE_URL}/mitid/complete-login"
CHAT_URL = f"{BASE_URL}/chat"


DEMO_USER_ID = "mette-demo"


test_cases = [
    {
        "category": "personal_logged_in",
        "question": "Hvor meget har jeg stående på min pension?",
        "must_not_contain": ["Du skal være logget ind"],
        "must_contain_any": ["pension", "opsparing", "stående"],
    },
    {
        "category": "personal_logged_in",
        "question": "Hvordan er min pension investeret?",
        "must_not_contain": ["Du skal være logget ind"],
        "must_contain_any": ["investeret", "risiko", "aktier", "obligationer"],
    },
    {
        "category": "personal_logged_in",
        "question": "Hvad er min risikoprofil?",
        "must_not_contain": ["Du skal være logget ind"],
        "must_contain_any": ["risikoprofil", "risiko"],
    },
    {
        "category": "personal_logged_in",
        "question": "Hvilke forsikringer har jeg?",
        "must_not_contain": ["Du skal være logget ind"],
        "must_contain_any": ["forsikring", "dækning", "kritisk sygdom"],
    },
]


def login() -> str | None:
    try:
        response = requests.post(
            LOGIN_URL,
            json={"user_id": DEMO_USER_ID},
            timeout=30,
        )

        if response.status_code != 200:
            print("Login fejlede")
            print("Status:", response.status_code)
            print("Svar:", response.text)
            return None

        data = response.json()
        return data.get("session_id")

    except requests.exceptions.RequestException as e:
        print("Fejl ved login:", e)
        return None


def call_chat(question: str, session_id: str) -> dict:
    try:
        response = requests.post(
            CHAT_URL,
            json={
                "message": question,
                "session_id": session_id,
            },
            timeout=120,
        )

        try:
            data = response.json()
        except Exception:
            data = {}

        return {
            "status_code": response.status_code,
            "reply": data.get("reply", ""),
            "sources": data.get("sources", []),
            "provider": data.get("provider"),
            "fallback_used": data.get("fallback_used"),
            "error": None if response.ok else response.text,
        }

    except requests.exceptions.RequestException as e:
        return {
            "status_code": None,
            "reply": "",
            "sources": [],
            "provider": None,
            "fallback_used": None,
            "error": str(e),
        }


def contains_any(reply: str, words: list[str]) -> bool:
    reply_lower = reply.lower()

    return any(word.lower() in reply_lower for word in words)


def contains_none(reply: str, words: list[str]) -> bool:
    reply_lower = reply.lower()

    return all(word.lower() not in reply_lower for word in words)


def main() -> None:
    print("\nKører personal-login-tests...\n")
    print("Backend skal køre på http://127.0.0.1:8000\n")

    session_id = login()

    if not session_id:
        print("Kunne ikke køre tests, fordi login fejlede.")
        return

    print("Login lykkedes.")
    print("Session oprettet.\n")

    passed_count = 0

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        must_not_contain = test_case["must_not_contain"]
        must_contain_any = test_case["must_contain_any"]

        result = call_chat(question, session_id)
        reply = result["reply"]

        status_ok = result["status_code"] == 200
        has_reply = bool(reply)
        does_not_reject_login = contains_none(reply, must_not_contain)
        has_relevant_content = contains_any(reply, must_contain_any)
        no_error = result["error"] is None

        passed = (
            status_ok
            and has_reply
            and does_not_reject_login
            and has_relevant_content
            and no_error
        )

        if passed:
            passed_count += 1

        print("=" * 80)
        print(f"Test {index}")
        print(f"Kategori: {test_case['category']}")
        print(f"Spørgsmål: {question}")
        print(f"Status code: {result['status_code']}")
        print(f"Provider: {result['provider']}")
        print(f"Fallback brugt: {result['fallback_used']}")
        print(f"Afviser login forkert: {not does_not_reject_login}")
        print(f"Relevant indhold: {has_relevant_content}")
        print(f"Bestået: {passed}")

        if result["error"]:
            print("Fejl:", result["error"])

        print("Svar:", reply)

    total = len(test_cases)
    pass_rate = round((passed_count / total) * 100, 2)

    print("\n" + "=" * 80)
    print("SAMLET RESULTAT")
    print(f"Bestået: {passed_count}/{total}")
    print(f"Pass rate: {pass_rate}%")


if __name__ == "__main__":
    main()

    