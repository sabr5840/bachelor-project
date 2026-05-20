import requests

BASE_URL = "http://127.0.0.1:8000"

print("Kører rate limit test...\n")

successful_requests = 0
rate_limited = False

for i in range(11):
    response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": f"Test besked {i}",
            "history": []
        }
    )

    print(f"Request {i + 1}: Status {response.status_code}")

    if response.status_code == 200:
        successful_requests += 1

    if response.status_code == 429:
        rate_limited = True
        print("Rate limiting aktiveret korrekt.")
        print("Svar:", response.json())

print("\n==============================")
print(f"Succesfulde requests: {successful_requests}")
print(f"Rate limiting aktiveret: {rate_limited}")
print("==============================")