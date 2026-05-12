import requests


URL = "http://127.0.0.1:8000/chat"


test_cases = [
    {
        "question": "Hvad er ratepension?",
        "expected_source": "pensionstype_ratepension.txt",
    },
    {
        "question": "Hvad er livrente?",
        "expected_source": "pensionstype_livsrente.txt",
    },
    {
        "question": "Hvad er aldersopsparing?",
        "expected_source": "pensionstype_aldersopsparing.txt",
    },
    {
        "question": "Hvad er PAL-skat?",
        "expected_source": "skat_pensionsafkastskat.txt",
    },
    {
        "question": "Hvordan beskattes pension ved udbetaling?",
        "expected_source": "skat_udbetaling.txt",
    },
    {
        "question": "Hvordan fungerer skat ved indbetaling til pension?",
        "expected_source": "skat_indbetaling.txt",
    },
    {
        "question": "Hvordan er pension investeret?",
        "expected_source": "investering_overblik.txt",
    },
    {
        "question": "Hvad betyder afkast på pension?",
        "expected_source": "investering_afkast.txt",
    },
    {
        "question": "Hvad sker der med min pension, hvis jeg skifter job?",
        "expected_source": "situation_nyt_job.txt",
    },
    {
        "question": "Hvordan anmelder jeg kritisk sygdom?",
        "expected_source": "situation_kritisk_sygdom.txt",
    },
    {
        "question": "Kan man samle sine pensioner?",
        "expected_source": "situation_samle_pension.txt",
    },
    {
        "question": "Hvem får min pension, hvis jeg dør?",
        "expected_source": "doedsfald_begunstigelse.txt",
    },
    {
        "question": "Hvad er folkepension?",
        "expected_source": "folkepension_overblik.txt",
    },
    {
        "question": "Hvad er ATP pension?",
        "expected_source": "atp_pension_overblik.txt",
    },
]


def call_api(question: str) -> dict:
    response = requests.post(
        URL,
        json={"message": question},
        timeout=120,
    )

    data = response.json()

    return {
        "status_code": response.status_code,
        "reply": data.get("reply", ""),
        "sources": [
            source.get("filename", "")
            for source in data.get("sources", [])
        ],
    }


def main() -> None:
    passed = 0

    print("\nKører retrieval-tests...\n")

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_source = test_case["expected_source"]

        result = call_api(question)
        actual_sources = result["sources"]

        source_found = expected_source in actual_sources
        test_passed = result["status_code"] == 200 and source_found

        if test_passed:
            passed += 1

        print("=" * 80)
        print(f"Test {index}")
        print(f"Spørgsmål: {question}")
        print(f"Forventet kilde: {expected_source}")
        print(f"Fundne kilder: {actual_sources}")
        print(f"Bestået: {test_passed}")

    total = len(test_cases)
    pass_rate = round((passed / total) * 100, 2)

    print("\n" + "=" * 80)
    print("SAMLET RESULTAT")
    print(f"Bestået: {passed}/{total}")
    print(f"Pass rate: {pass_rate}%")


if __name__ == "__main__":
    main()