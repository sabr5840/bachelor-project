import time
from concurrent.futures import ThreadPoolExecutor

import requests


URL = "http://127.0.0.1:8000/chat"

PAYLOAD = {
    "message": "Hvad er ratepension?"
}

TOTAL_REQUESTS = 50
CONCURRENT_USERS = 10


def send_request(request_number: int) -> dict:
    start_time = time.time()

    try:
        response = requests.post(
            URL,
            json=PAYLOAD,
            timeout=120,
        )

        response_time = round(time.time() - start_time, 2)

        return {
            "request_number": request_number,
            "status_code": response.status_code,
            "success": response.status_code == 200,
            "response_time": response_time,
            "error": None,
        }

    except requests.exceptions.RequestException as error:
        response_time = round(time.time() - start_time, 2)

        return {
            "request_number": request_number,
            "status_code": None,
            "success": False,
            "response_time": response_time,
            "error": str(error),
        }


def main() -> None:
    print("\nStarter load test...")
    print(f"Total requests: {TOTAL_REQUESTS}")
    print(f"Samtidige brugere: {CONCURRENT_USERS}")
    print("Backend skal køre på http://127.0.0.1:8000")

    start_time = time.time()

    with ThreadPoolExecutor(max_workers=CONCURRENT_USERS) as executor:
        results = list(
            executor.map(
                send_request,
                range(1, TOTAL_REQUESTS + 1),
            )
        )

    total_time = round(time.time() - start_time, 2)

    successful_requests = sum(1 for result in results if result["success"])
    failed_requests = TOTAL_REQUESTS - successful_requests

    response_times = [result["response_time"] for result in results]

    average_response_time = round(sum(response_times) / len(response_times), 2)
    fastest_response_time = min(response_times)
    slowest_response_time = max(response_times)
    error_rate = round((failed_requests / TOTAL_REQUESTS) * 100, 2)

    print("\nRESULTAT")
    print("=" * 60)
    print(f"Succesfulde requests: {successful_requests}/{TOTAL_REQUESTS}")
    print(f"Fejlede requests: {failed_requests}/{TOTAL_REQUESTS}")
    print(f"Fejlrate: {error_rate}%")
    print(f"Gennemsnitlig svartid: {average_response_time} sekunder")
    print(f"Hurtigste svartid: {fastest_response_time} sekunder")
    print(f"Langsomste svartid: {slowest_response_time} sekunder")
    print(f"Samlet tid: {total_time} sekunder")

    if failed_requests > 0:
        print("\nFejlede requests:")
        for result in results:
            if not result["success"]:
                print(
                    f"Request {result['request_number']}: "
                    f"status={result['status_code']}, "
                    f"error={result['error']}"
                )


if __name__ == "__main__":
    main()