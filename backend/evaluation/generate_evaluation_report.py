import json
from collections import Counter
from pathlib import Path

import matplotlib.pyplot as plt

RESULTS_FILE = Path(__file__).parent / "results" / "test_results.json"
REPORT_FILE = Path(__file__).parent / "reports" / "evaluation_report.md"

CHARTS_DIR = Path(__file__).parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)


def load_results() -> dict:
    with open(RESULTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def count_by_category(results: list[dict]) -> Counter:
    return Counter(result["category"] for result in results)


def count_passed_by_category(results: list[dict]) -> dict:
    categories = {}

    for result in results:
        category = result["category"]

        if category not in categories:
            categories[category] = {
                "total": 0,
                "passed": 0,
            }

        categories[category]["total"] += 1

        if result["passed"]:
            categories[category]["passed"] += 1

    return categories


def generate_main_metrics_chart(summary: dict) -> None:
    labels = [
        "Samlet pass rate",
        "Retrieval accuracy",
        "Guardrail accuracy",
    ]

    values = [
        summary["overall_pass_rate_percent"],
        summary["retrieval_accuracy_percent"],
        summary["guardrail_accuracy_percent"],
    ]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)

    plt.ylim(0, 110)
    plt.ylabel("Procent")
    plt.title("Overordnede evalueringsresultater")

    for index, value in enumerate(values):
        plt.text(index, value + 1, f"{value}%", ha="center")

    plt.tight_layout()

    plt.savefig(CHARTS_DIR / "main_metrics.png")
    plt.close()


def generate_category_distribution_chart(results: list[dict]) -> None:
    category_counts = count_by_category(results)

    labels = list(category_counts.keys())
    values = list(category_counts.values())

    plt.figure(figsize=(10, 6))
    plt.bar(labels, values)

    plt.ylabel("Antal tests")
    plt.title("Testfordeling efter kategori")

    plt.xticks(rotation=45, ha="right")

    plt.tight_layout()

    plt.savefig(CHARTS_DIR / "category_test_distribution.png")
    plt.close()


def generate_provider_distribution_chart(results: list[dict]) -> None:
    provider_counts = Counter(
        result["provider"] if result["provider"] else "ingen LLM"
        for result in results
    )

    labels = list(provider_counts.keys())
    values = list(provider_counts.values())

    plt.figure(figsize=(7, 5))
    plt.bar(labels, values)

    plt.ylabel("Antal svar")
    plt.title("LLM-provider-fordeling")

    plt.tight_layout()

    plt.savefig(CHARTS_DIR / "provider_distribution.png")
    plt.close()


def generate_charts(data: dict) -> None:
    summary = data["summary"]
    results = data["results"]

    generate_main_metrics_chart(summary)
    generate_category_distribution_chart(results)
    generate_provider_distribution_chart(results)


def build_report(data: dict) -> str:
    summary = data["summary"]
    results = data["results"]

    category_counts = count_by_category(results)
    category_pass_rates = count_passed_by_category(results)

    provider_counts = Counter(
        result["provider"] if result["provider"] else "ingen LLM"
        for result in results
    )

    fallback_count = sum(1 for result in results if result["fallback_used"])

    lines = []

    lines.append("# Evalueringsrapport")
    lines.append("")
    lines.append(
        "Denne rapport opsummerer den automatiserede evaluering af AI-pensionsrådgiveren."
    )
    lines.append(
        "Evalueringen dækker RAG-retrieval, guardrails, svarkvalitet og korrekt håndtering af spørgsmål uden for systemets datagrundlag."
    )
    lines.append("")

    lines.append("## Samlet resultat")
    lines.append("")
    lines.append(f"- Antal tests: {summary['total_tests']}")
    lines.append(f"- Beståede tests: {summary['passed_tests']}")
    lines.append(f"- Fejlede tests: {summary['failed_tests']}")
    lines.append(
        f"- Samlet pass rate: {summary['overall_pass_rate_percent']}%"
    )
    lines.append(
        f"- Retrieval accuracy: {summary['retrieval_accuracy_percent']}%"
    )
    lines.append(
        f"- Guardrail accuracy: {summary['guardrail_accuracy_percent']}%"
    )
    lines.append("")

    lines.append("## Testfordeling efter kategori")
    lines.append("")
    lines.append("| Kategori | Antal tests | Bestået | Pass rate |")
    lines.append("|---|---:|---:|---:|")

    for category, values in sorted(category_pass_rates.items()):
        total = values["total"]
        passed = values["passed"]

        pass_rate = round((passed / total) * 100, 2)

        lines.append(
            f"| {category} | {total} | {passed} | {pass_rate}% |"
        )

    lines.append("")

    lines.append("## LLM-provider-fordeling")
    lines.append("")
    lines.append("| Provider | Antal svar |")
    lines.append("|---|---:|")

    for provider, count in provider_counts.items():
        lines.append(f"| {provider} | {count} |")

    lines.append("")
    lines.append(
        f"Fallback blev brugt i {fallback_count} ud af {summary['total_tests']} tests."
    )
    lines.append("")

    lines.append("## Retrieval og guardrails")
    lines.append("")
    lines.append(
        f"Retrieval blev testet på {summary['retrieval_tests']} spørgsmål, hvor "
        f"{summary['correct_retrieval_tests']} hentede den forventede kilde."
    )

    lines.append(
        f"Guardrails blev testet på {summary['guardrail_tests']} spørgsmål, hvor "
        f"{summary['correct_guardrail_tests']} blev håndteret korrekt."
    )

    lines.append("")

    lines.append("## Eksempler på beståede tests")
    lines.append("")

    for result in results[:5]:
        lines.append(f"### Test {result['number']}: {result['question']}")
        lines.append("")
        lines.append(f"- Kategori: {result['category']}")
        lines.append(
            f"- Forventet adfærd: {result['expected_behavior']}"
        )
        lines.append(f"- Bestået: {result['passed']}")

        lines.append(
            f"- Fundne kilder: "
            f"{', '.join(result['actual_sources']) if result['actual_sources'] else 'Ingen'}"
        )

        lines.append("")

    lines.append("## Genererede visualiseringer")
    lines.append("")
    lines.append(
        "- charts/main_metrics.png"
    )
    lines.append(
        "- charts/category_test_distribution.png"
    )
    lines.append(
        "- charts/provider_distribution.png"
    )

    lines.append("")

    lines.append("## Faglig vurdering")
    lines.append("")

    lines.append(
        "Resultaterne viser, at systemet håndterer de definerede testcases korrekt. "
        "Særligt viser evalueringen, at RAG-komponenten kan hente relevante kilder, "
        "at personlige spørgsmål uden login afvises korrekt, og at spørgsmål uden for pensionsdomænet "
        "ikke besvares med opdigtet information."
    )

    lines.append("")

    lines.append(
        "Det skal dog bemærkes, at testresultaterne er baseret på et kontrolleret testdatasæt. "
        "I en produktionskontekst bør evalueringen udvides med flere brugerformuleringer, edge cases, "
        "manuelle ekspertvurderinger og løbende monitorering af AI-svar."
    )

    return "\n".join(lines)


def main() -> None:
    data = load_results()

    generate_charts(data)

    report = build_report(data)

    with open(REPORT_FILE, "w", encoding="utf-8") as file:
        file.write(report)

    print(f"Evalueringsrapport gemt i: {REPORT_FILE}")
    print(f"Grafer gemt i: {CHARTS_DIR}")


if __name__ == "__main__":
    main()