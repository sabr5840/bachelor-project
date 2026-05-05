import json
from pathlib import Path

import requests


URL = "http://127.0.0.1:8000/chat"
OUTPUT_FILE = Path(__file__).parent / "test_results.json"


test_cases = [
    {
        "question": "Hvad er ratepension?",
        "expected_sources": ["pensionstype_ratepension.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er livrente?",
        "expected_sources": ["pensionstype_livsrente.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er aldersopsparing?",
        "expected_sources": ["pensionstype_aldersopsparing.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er forskellen på ratepension, livrente og aldersopsparing?",
        "expected_sources": ["pensionstyper_sammenligning.txt"],
        "expected_behavior": "comparison",
    },
    {
        "question": "Hvad er forskellen på ratepension og livrente?",
        "expected_sources": ["pensionstyper_sammenligning.txt", "pension_udbetaling_forskelle.txt"],
        "expected_behavior": "comparison",
    },
    {
        "question": "Hvad er PAL-skat?",
        "expected_sources": ["skat_pensionsafkastskat.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvordan beskattes pension ved udbetaling?",
        "expected_sources": ["skat_udbetaling.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvordan fungerer skat ved indbetaling til pension?",
        "expected_sources": ["skat_indbetaling.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvorfor er noget pension skattefrit ved udbetaling?",
        "expected_sources": ["skat_udbetaling.txt", "pensionstyper_sammenligning.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvordan påvirker pension folkepension og offentlige ydelser?",
        "expected_sources": ["skat_modregning.txt", "modregning_overblik.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Er der loft for indbetaling til pension?",
        "expected_sources": ["pension_indbetaling_lofter.txt", "indbetaling_og_lofter.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Kan jeg indbetale ekstra til pension?",
        "expected_sources": ["pension_indbetaling_overblik.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvad sker der, hvis jeg indbetaler for meget til pension?",
        "expected_sources": ["pension_indbetaling_for_meget.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Kan jeg få pension udbetalt før pensionsalderen?",
        "expected_sources": ["pension_udbetaling_foer_tid.txt", "pension_udbetaling_overblik.txt"],
        "expected_behavior": "semi",
    },
    {
        "question": "Hvad er genkøb af pension?",
        "expected_sources": ["pension_udbetaling_foer_tid.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Kan pension udbetales som engangsbeløb?",
        "expected_sources": ["pension_udbetaling_forskelle.txt", "pension_udbetaling_overblik.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvor længe kan pension udbetales?",
        "expected_sources": ["pension_udbetaling_forskelle.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvad er folkepension?",
        "expected_sources": ["folkepension_overblik.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvornår kan man få folkepension?",
        "expected_sources": ["folkepensionsalder_overblik.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvad er ATP pension?",
        "expected_sources": ["atp_pension_overblik.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er seniorpension?",
        "expected_sources": ["seniorpension.txt", "seniorpension_overblik.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er tidlig pension?",
        "expected_sources": ["tidlig_pension.txt", "tidlig_pension_betingelser.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er førtidspension?",
        "expected_sources": ["foertidspension_vilkaar.txt", "situation_foertidspension.txt"],
        "expected_behavior": "definition",
    },
    {
        "question": "Hvad er forskellen på førtidspension, seniorpension og tidlig pension?",
        "expected_sources": ["foertid_vs_senior_vs_tidlig_pension.txt", "pension_regler_generelt.txt"],
        "expected_behavior": "comparison",
    },
    {
        "question": "Kan jeg samle mine pensioner?",
        "expected_sources": ["situation_samle_pension.txt"],
        "expected_behavior": "semi",
    },
    {
        "question": "Hvad sker der med min pension, hvis jeg skifter job?",
        "expected_sources": ["situation_nyt_job.txt"],
        "expected_behavior": "semi",
    },
    {
        "question": "Jeg er blevet syg, hvad gør jeg?",
        "expected_sources": ["situation_sygdom.txt"],
        "expected_behavior": "semi",
    },
    {
        "question": "Hvordan anmelder jeg kritisk sygdom?",
        "expected_sources": ["situation_kritisk_sygdom.txt"],
        "expected_behavior": "semi",
    },
    {
        "question": "Hvem får min pension, hvis jeg dør?",
        "expected_sources": ["doedsfald_begunstigelse.txt", "doedsfald_overblik.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvordan er pension investeret?",
        "expected_sources": ["investering_overblik.txt"],
        "expected_behavior": "general",
    },
    {
        "question": "Hvad er moms?",
        "expected_sources": [],
        "expected_behavior": "out_of_scope",
    },
]


def call_api(question: str) -> dict:
    try:
        response = requests.post(URL, json={"message": question}, timeout=120)

        if response.status_code != 200:
            return {
                "reply": "",
                "sources": [],
                "error": f"HTTP {response.status_code}: {response.text}",
            }

        data = response.json()

        return {
            "reply": data.get("reply", ""),
            "sources": [source.get("filename", "") for source in data.get("sources", [])],
            "error": None,
        }

    except requests.exceptions.Timeout:
        return {
            "reply": "",
            "sources": [],
            "error": "Request timed out",
        }

    except requests.exceptions.RequestException as e:
        return {
            "reply": "",
            "sources": [],
            "error": str(e),
        }


def evaluate_sources(expected_sources: list[str], actual_sources: list[str]) -> bool | None:
    if not expected_sources:
        return None

    return any(expected in actual_sources for expected in expected_sources)


def main() -> None:
    results = []

    print("\nKører RAG-test...\n")

    for index, test_case in enumerate(test_cases, start=1):
        question = test_case["question"]
        expected_sources = test_case["expected_sources"]

        api_result = call_api(question)

        actual_sources = api_result["sources"]
        source_match = evaluate_sources(expected_sources, actual_sources)

        result = {
            "number": index,
            "question": question,
            "expected_sources": expected_sources,
            "actual_sources": actual_sources,
            "source_match": source_match,
            "expected_behavior": test_case["expected_behavior"],
            "reply": api_result["reply"],
            "error": api_result["error"],
        }

        results.append(result)

        print("=" * 80)
        print(f"Test {index}: {question}")
        print(f"Forventede kilder: {expected_sources if expected_sources else 'Ingen fast forventet kilde'}")
        print(f"Fundne kilder: {actual_sources}")
        print(f"Kilde-match: {source_match if source_match is not None else 'Ikke vurderet'}")

        if api_result["error"]:
            print(f"Fejl: {api_result['error']}")

        print(f"Svar: {api_result['reply']}")

    scored_results = [result for result in results if result["source_match"] is not None]
    correct_results = [result for result in scored_results if result["source_match"] is True]

    accuracy = (
        round(len(correct_results) / len(scored_results) * 100, 2)
        if scored_results
        else None
    )

    summary = {
        "total_tests": len(results),
        "scored_tests": len(scored_results),
        "correct_source_matches": len(correct_results),
        "source_accuracy_percent": accuracy,
    }

    output = {
        "summary": summary,
        "results": results,
    }

    with open(OUTPUT_FILE, "w", encoding="utf-8") as file:
        json.dump(output, file, ensure_ascii=False, indent=2)

    print("\n" + "=" * 80)
    print("SAMLET RESULTAT")
    print(f"Antal tests: {summary['total_tests']}")
    print(f"Tests med forventet kilde: {summary['scored_tests']}")
    print(f"Korrekte kilde-match: {summary['correct_source_matches']}")

    if accuracy is not None:
        print(f"Retrieval accuracy: {accuracy}%")

    print(f"Resultater gemt i: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()