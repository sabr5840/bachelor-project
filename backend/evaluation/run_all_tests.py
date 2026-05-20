import os
import subprocess
from pathlib import Path

BASE_DIR = Path(__file__).parent

TEST_FILES = [
    "tests/security/test_sessions.py",
    "tests/security/test_personal_login.py",
    "tests/security/test_guardrails.py",
    "tests/rag/test_retrieval.py",
    "tests/rag/test_rag.py",
    "tests/rag/test_response_quality.py",
    "tests/resilience/test_llm_fallback.py",
    "tests/performance/test_load.py",
]


def run_test_file(filename: str) -> dict:
    path = BASE_DIR / filename

    print("\n" + "=" * 90)
    print(f"Kører: {filename}")
    print("=" * 90)

    env = os.environ.copy()
    env["DISABLE_RATE_LIMIT"] = "true"

    result = subprocess.run(
        ["python3", str(path)],
        capture_output=True,
        text=True,
        env=env,
    )

    print(result.stdout)

    if result.stderr:
        print("FEJL/STDERR:")
        print(result.stderr)

    return {
        "file": filename,
        "return_code": result.returncode,
        "passed": result.returncode == 0,
    }


def main() -> None:
    print("\nKører samlet evaluering af bachelorprojektet")
    print("Backend skal køre på http://127.0.0.1:8000\n")
    print("Rate limiting er deaktiveret under samlet evaluering.\n")

    results = []

    for test_file in TEST_FILES:
        results.append(run_test_file(test_file))

    passed = sum(1 for result in results if result["passed"])
    total = len(results)

    print("\n" + "=" * 90)
    print("SAMLET EVALUERINGSRESULTAT")
    print("=" * 90)

    for result in results:
        status = "BESTÅET" if result["passed"] else "FEJLET"
        print(f"{result['file']}: {status}")

    print("-" * 90)
    print(f"Beståede testfiler: {passed}/{total}")
    print(f"Samlet pass rate: {round((passed / total) * 100, 2)}%")


if __name__ == "__main__":
    main()