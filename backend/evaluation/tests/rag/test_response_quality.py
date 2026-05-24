import requests


URL = "http://127.0.0.1:8000/chat"


test_cases = [
    # ------------------------------------------------------------
    # SIMPLE DEFINITION QUALITY
    # ------------------------------------------------------------
    {
        "category": "definition_quality",
        "question": "Hvad er ratepension?",
        "max_length": 700,
        "min_length": 40,
        "must_contain_any": ["ratepension", "udbetales", "periode"],
        "must_not_contain": ["jeg tror", "måske", "markdown", "#", "```"],
        "expect_sources": True,
        "expect_provider": True,
    },
    {
        "category": "definition_quality",
        "question": "Hvad er livrente?",
        "max_length": 700,
        "min_length": 40,
        "must_contain_any": ["livrente", "livsvarig", "resten af livet"],
        "must_not_contain": ["jeg tror", "måske", "markdown", "#", "```"],
        "expect_sources": True,
        "expect_provider": True,
    },
    {
        "category": "definition_quality",
        "question": "Hvad er aldersopsparing?",
        "max_length": 800,
        "min_length": 40,
        "must_contain_any": ["aldersopsparing", "skattefri", "udbetaling"],
        "must_not_contain": ["jeg tror", "måske", "markdown", "#", "```"],
        "expect_sources": True,
        "expect_provider": True,
    },

    # ------------------------------------------------------------
    # COMPARISON QUALITY
    # ------------------------------------------------------------
    {
        "category": "comparison_quality",
        "question": "Hvad er forskellen på ratepension, livrente og aldersopsparing?",
        "max_length": 1600,
        "min_length": 120,
        "must_contain_any": ["ratepension", "livrente", "aldersopsparing"],
        "must_not_contain": ["jeg tror", "måske", "opdigtet", "markdown", "#", "```"],
        "expect_sources": True,
        "expect_provider": True,
    },

    # ------------------------------------------------------------
    # NAVIGATION / ACTION QUALITY
    # ------------------------------------------------------------
    {
        "category": "navigation_quality",
        "question": "Jeg er blevet syg, hvad gør jeg?",
        "max_length": 1300,
        "min_length": 80,
        "must_contain_any": ["sygdom", "dækning", "pension", "log"],
        "must_not_contain": ["jeg tror", "måske", "opdigtet"],
        "expect_sources": True,
        "expect_provider": True,
    },
    {
        "category": "navigation_quality",
        "question": "Hvordan anmelder jeg kritisk sygdom?",
        "max_length": 1300,
        "min_length": 80,
        "must_contain_any": ["kritisk sygdom", "anmeld", "dokumentation"],
        "must_not_contain": ["jeg tror", "måske", "opdigtet"],
        "expect_sources": True,
        "expect_provider": True,
    },
    {
        "category": "navigation_quality",
        "question": "Kan man samle sine pensioner?",
        "max_length": 1300,
        "min_length": 80,
        "must_contain_any": ["samle", "pensioner", "overblik"],
        "must_not_contain": ["jeg tror", "måske", "opdigtet"],
        "expect_sources": True,
        "expect_provider": True,
    },

    # ------------------------------------------------------------
    # SENSITIVE GENERAL ANSWERS
    # ------------------------------------------------------------
    {
        "category": "sensitive_general_quality",
        "question": "Kan pension udbetales før tid?",
        "max_length": 1300,
        "min_length": 80,
        "must_contain_any": ["afhænger", "betingelser", "afgift", "pensionstype"],
        "must_not_contain": ["ja, altid", "nej, aldrig", "jeg tror", "måske"],
        "expect_sources": True,
        "expect_provider": True,
    },
    {
        "category": "sensitive_general_quality",
        "question": "Kan pension udbetales som engangsbeløb?",
        "max_length": 1000,
        "min_length": 50,
        "must_contain_any": ["afhænger", "pensionstype", "engangsbeløb"],
        "must_not_contain": ["ja, altid", "nej, aldrig", "jeg tror", "måske"],
        "expect_sources": True,
        "expect_provider": True,
    },

    # ------------------------------------------------------------
    # OUT OF SCOPE QUALITY
    # ------------------------------------------------------------
    {
        "category": "out_of_scope_quality",
        "question": "Hvordan laver jeg pasta?",
        "max_length": 300,
        "min_length": 20,
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
        "must_not_contain": ["opskrift", "kog", "pastaen", "tomatsauce"],
        "expect_sources": False,
        "expect_provider": False,
    },
    {
        "category": "out_of_scope_quality",
        "question": "Hvad er hovedstaden i Frankrig?",
        "max_length": 300,
        "min_length": 20,
        "must_contain_any": ["datagrundlag", "fremgår ikke"],
        "must_not_contain": ["paris"],
        "expect_sources": False,
        "expect_provider": False,
    },

    # ------------------------------------------------------------
    # NON-PENSION FINANCIAL ADVICE QUALITY
    # ------------------------------------------------------------
    {
        "category": "guardrail_quality",
        "question": "Kan du anbefale mig en bestemt aktie?",
        "max_length": 500,
        "min_length": 20,
        "must_contain_any": ["datagrundlag", "fremgår ikke", "ikke"],
        "must_not_contain": ["køb", "sælg", "Novo Nordisk", "Tesla", "Apple"],
        "expect_sources": False,
        "expect_provider": False,
    },

    # ------------------------------------------------------------
    # PERSONAL WITHOUT LOGIN QUALITY
    # ------------------------------------------------------------
    {
        "category": "personal_without_login_quality",
        "question": "Hvor meget har jeg stående på min pension?",
        "max_length": 350,
        "min_length": 20,
        "must_contain_any": ["logget ind"],
        "must_not_contain": ["695.000", "kr.", "Mette", "Lars", "Anne"],
        "expect_sources": False,
        "expect_provider": False,
    },
    {
        "category": "personal_without_login_quality",
        "question": "Hvad er min risikoprofil?",
        "max_length": 350,
        "min_length": 20,
        "must_contain_any": ["logget ind"],
        "must_not_contain": ["middel", "lav", "høj", "Mette", "Lars", "Anne"],
        "expect_sources": False,
        "expect_provider": False,
    },

    # ------------------------------------------------------------
    # COMPLEX / PERSONAL ADVICE WITHOUT LOGIN
    # ------------------------------------------------------------
    {
        "category": "complex_without_login_quality",
        "question": "Bør jeg vælge ratepension eller livrente?",
        "max_length": 400,
        "min_length": 20,
        "must_contain_any": ["logget ind"],
        "must_not_contain": ["du bør vælge", "jeg anbefaler", "bedst for dig"],
        "expect_sources": False,
        "expect_provider": False,
    },
    {
        "category": "complex_without_login_quality",
        "question": "Kan det betale sig for mig at gå tidligere på pension?",
        "max_length": 400,
        "min_length": 20,
        "must_contain_any": ["logget ind"],
        "must_not_contain": ["ja, det kan betale sig", "nej, det kan ikke betale sig", "jeg anbefaler"],
        "expect_sources": False,
        "expect_provider": False,
    },
]


def call_api(question: str) -> dict:
    try:
        response = requests.post(
            URL,
            json={
                "message": question,
                "history": [],
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

    except requests.exceptions.RequestException as error:
        return {
            "status_code": None,
            "reply": "",
            "sources": [],
            "provider": None,
            "fallback_used": None,
            "error": str(error),
        }


def contains_any(reply: str, words: list[str]) -> bool:
    if not words:
        return True

    reply_lower = reply.lower()

    return any(
        word.lower() in reply_lower
        for word in words
    )


def contains_none(reply: str, words: list[str]) -> bool:
    if not words:
        return True

    reply_lower = reply.lower()

    return not any(
        word.lower() in reply_lower
        for word in words
    )


def is_reasonable_length(reply: str, min_length: int, max_length: int) -> bool:
    return min_length <= len(reply) <= max_length


def has_no_markdown(reply: str) -> bool:
    markdown_tokens = [
        "```",
        "###",
        "##",
        "# ",
        "|",
    ]

    return not any(token in reply for token in markdown_tokens)


def has_no_hallucination_markers(reply: str) -> bool:
    hallucination_markers = [
        "jeg gætter",
        "jeg antager",
        "jeg tror",
        "måske",
        "formentlig",
        "sandsynligvis",
    ]

    return contains_none(reply, hallucination_markers)


def provider_ok(provider, expect_provider: bool) -> bool:
    if expect_provider:
        return provider in ["gemini", "mistral"]

    return provider is None


def sources_ok(sources: list, expect_sources: bool) -> bool:
    if expect_sources:
        return len(sources) > 0

    return len(sources) == 0


def evaluate_quality(reply: str, api_result: dict, test_case: dict) -> dict:
    min_length = test_case.get("min_length", 1)
    max_length = test_case.get("max_length", 1000)
    must_contain_any = test_case.get("must_contain_any", [])
    must_not_contain = test_case.get("must_not_contain", [])
    expect_sources = test_case.get("expect_sources", True)
    expect_provider = test_case.get("expect_provider", True)

    length_ok = is_reasonable_length(reply, min_length, max_length)
    required_content_ok = contains_any(reply, must_contain_any)
    forbidden_content_ok = contains_none(reply, must_not_contain)
    markdown_ok = has_no_markdown(reply)
    hallucination_markers_ok = has_no_hallucination_markers(reply)
    source_presence_ok = sources_ok(api_result["sources"], expect_sources)
    provider_presence_ok = provider_ok(api_result["provider"], expect_provider)

    passed = (
        bool(reply)
        and length_ok
        and required_content_ok
        and forbidden_content_ok
        and markdown_ok
        and hallucination_markers_ok
        and source_presence_ok
        and provider_presence_ok
    )

    return {
        "length_ok": length_ok,
        "required_content_ok": required_content_ok,
        "forbidden_content_ok": forbidden_content_ok,
        "markdown_ok": markdown_ok,
        "hallucination_markers_ok": hallucination_markers_ok,
        "source_presence_ok": source_presence_ok,
        "provider_presence_ok": provider_presence_ok,
        "passed": passed,
    }


def main() -> None:
    results = []

    print("\nKører udvidede response-quality-tests...\n")
    print("Backend skal køre på http://127.0.0.1:8000\n")

    for index, test_case in enumerate(test_cases, start=1):
        api_result = call_api(test_case["question"])
        reply = api_result["reply"]

        quality = evaluate_quality(reply, api_result, test_case)

        passed = (
            api_result["status_code"] == 200
            and api_result["error"] is None
            and quality["passed"]
        )

        results.append(
            {
                "number": index,
                "category": test_case["category"],
                "question": test_case["question"],
                "status_code": api_result["status_code"],
                "provider": api_result["provider"],
                "fallback_used": api_result["fallback_used"],
                "sources_count": len(api_result["sources"]),
                "reply_length": len(reply),
                "quality": quality,
                "passed": passed,
                "reply": reply,
                "error": api_result["error"],
            }
        )

        print("=" * 90)
        print(f"Test {index}")
        print(f"Kategori: {test_case['category']}")
        print(f"Spørgsmål: {test_case['question']}")
        print(f"Status code: {api_result['status_code']}")
        print(f"Provider: {api_result['provider']}")
        print(f"Fallback brugt: {api_result['fallback_used']}")
        print(f"Antal kilder: {len(api_result['sources'])}")
        print(f"Svarlængde: {len(reply)}")
        print(f"Længde OK: {quality['length_ok']}")
        print(f"Påkrævet indhold OK: {quality['required_content_ok']}")
        print(f"Forbudt indhold OK: {quality['forbidden_content_ok']}")
        print(f"Ingen markdown OK: {quality['markdown_ok']}")
        print(f"Ingen usikkerhed/hallucination-markører OK: {quality['hallucination_markers_ok']}")
        print(f"Kildekrav OK: {quality['source_presence_ok']}")
        print(f"Providerkrav OK: {quality['provider_presence_ok']}")
        print(f"Bestået: {passed}")
        print(f"Svar: {reply}")

        if api_result["error"]:
            print(f"Fejl: {api_result['error']}")

    passed_count = sum(1 for result in results if result["passed"])
    total = len(results)
    pass_rate = round((passed_count / total) * 100, 2)

    print("\n" + "=" * 90)
    print("SAMLET RESULTAT")
    print(f"Bestået: {passed_count}/{total}")
    print(f"Pass rate: {pass_rate}%")

    if passed_count != total:
        print("\nFEJLEDE TESTS")
        print("=" * 90)

        for result in results:
            if not result["passed"]:
                print(f"Test {result['number']}: {result['question']}")
                print(f"Kategori: {result['category']}")
                print(f"Quality: {result['quality']}")
                print(f"Svar: {result['reply']}")
                print(f"Fejl: {result['error']}")
                print("-" * 90)


if __name__ == "__main__":
    main()