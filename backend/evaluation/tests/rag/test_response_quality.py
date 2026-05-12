import requests


URL = "http://127.0.0.1:8000/chat"


test_cases = [
    {
        "category": "definition_quality",
        "question": "Hvad er ratepension?",
        "max_length": 600,
        "must_not_contain": ["jeg tror", "måske", "markdown", "#"],
    },
    {
        "category": "definition_quality",
        "question": "Hvad er livrente?",
        "max_length": 600,
        "must_not_contain": ["jeg tror", "måske", "markdown", "#"],
    },
    {
        "category": "navigation_quality",
        "question": "Jeg er blevet syg, hvad gør jeg?",
        "max_length": 1200,
        "must_contain_any": ["log", "dækning", "sygdom"],
        "must_not_contain": ["jeg tror", "måske"],
    },
    {
        "category": "guardrail_quality",
        "question": "Kan du anbefale mig en bestemt aktie?",
        "max_length": 600,
        "must_contain_any": ["datagrundlag", "fremgår ikke", "ikke"],
    },
    {
        "category": "personal_without_login_quality",
        "question": "Hvor meget har jeg stående på min pension?",
        "max_length": 300,
        "must_contain_any": ["logget ind"],
    },
    {
        "category": "out_of_scope_quality",
        "question": "Hvordan laver jeg pasta?",
        "max_length": 300,
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
    },
]


def call_api(question: str) -> dict:
    try:
        response = requests.post(
            URL,
            json={"message": question},
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
    if not words:
        return True

    reply_lower = reply.lower()
    return any(word.lower() in reply_lower for word in words)


def contains_none(reply: str, words: list[str]) -> bool:
    reply_lower = reply.lower()
    return not any(word.lower() in reply_lower for word in words)


def is_reasonable_length(reply: str, max_length: int) -> bool:
    return len(reply) <= max_length


def has_no_markdown(reply: str) -> bool:
    markdown_tokens = ["```", "###", "##", "# ", "|"]
    return not any(token in reply for token in markdown_tokens)


def evaluate_quality(reply: str, test_case: dict) -> dict:
    max_length = test_case.get("max_length", 1000)
    must_contain_any = test_case.get("must_contain_any", [])
    must_not_contain = test_case.get("must_not_contain", [])

    length_ok = is_reasonable_length(reply, max_length)
    required_content_ok = contains_any(reply, must_contain_any)
    forbidden_content_ok = contains_none(reply, must_not_contain)
    markdown_ok = has_no_markdown(reply)

    passed = (
        bool(reply)
        and length_ok
        and required_content_ok
        and forbidden_content_ok
        and markdown_ok
    )

    return {
        "length_ok": length_ok,
        "required_content_ok": required_content_ok,
        "forbidden_content_ok": forbidden_content_ok,
        "markdown_ok": markdown_ok,
        "passed": passed,
    }


def main() -> None:
    results = []

    print("\nKører response-quality-tests...\n")
    print("Backend skal køre på http://127.0.0.1:8000\n")

    for index, test_case in enumerate(test_cases, start=1):
        api_result = call_api(test_case["question"])
        reply = api_result["reply"]

        quality = evaluate_quality(reply, test_case)

        passed = (
            api_result["status_code"] == 200
            and api_result["error"] is None
            and quality["passed"]
        )

        results.append(passed)

        print("=" * 80)
        print(f"Test {index}")
        print(f"Kategori: {test_case['category']}")
        print(f"Spørgsmål: {test_case['question']}")
        print(f"Status code: {api_result['status_code']}")
        print(f"Længde OK: {quality['length_ok']}")
        print(f"Påkrævet indhold OK: {quality['required_content_ok']}")
        print(f"Forbudt indhold OK: {quality['forbidden_content_ok']}")
        print(f"Ingen markdown OK: {quality['markdown_ok']}")
        print(f"Bestået: {passed}")
        print(f"Svar: {reply}")

        if api_result["error"]:
            print(f"Fejl: {api_result['error']}")

    passed_count = sum(results)
    total = len(results)

    print("\n" + "=" * 80)
    print("SAMLET RESULTAT")
    print(f"Bestået: {passed_count}/{total}")
    print(f"Pass rate: {round((passed_count / total) * 100, 2)}%")


if __name__ == "__main__":
    main()