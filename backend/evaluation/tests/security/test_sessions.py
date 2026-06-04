import requests


BASE_URL = "http://127.0.0.1:8000"
DEMO_USER_ID = "mette-demo"


def print_result(title: str, passed: bool, response=None):
    print("=" * 80)
    print(title)

    if response is not None:
        print("Status:", response.status_code)
        try:
            print("Svar:", response.json())
        except Exception:
            print("Svar:", response.text)

    print("Bestået:", passed)


def main():
    print("\nKører session-tests...\n")
    print("Backend skal køre på http://127.0.0.1:8000\n")

    passed_tests = 0
    total_tests = 0

    # ------------------------------------------------------------
    # Test 1: Login opretter session
    # ------------------------------------------------------------
    total_tests += 1

    login_response = requests.post(
        f"{BASE_URL}/mitid/complete-login",
        json={"user_id": DEMO_USER_ID},
        timeout=30,
    )

    login_data = login_response.json() if login_response.ok else {}
    session_id = login_data.get("session_id")

    passed = (
        login_response.status_code == 200
        and bool(session_id)
        and "customer" in login_data
        and "expires_at" in login_data
    )

    if passed:
        passed_tests += 1

    print_result("Test 1: Login opretter session", passed, login_response)

    if not session_id:
        print("\nKunne ikke fortsætte, fordi session_id mangler.")
        return

    # ------------------------------------------------------------
    # Test 2: Dashboard virker med gyldig session
    # ------------------------------------------------------------
    total_tests += 1

    dashboard_response = requests.get(
        f"{BASE_URL}/session/dashboard",
        params={"session_id": session_id},
        timeout=30,
    )

    passed = (
        dashboard_response.status_code == 200
        and isinstance(dashboard_response.json(), dict)
    )

    if passed:
        passed_tests += 1

    print_result("Test 2: Dashboard virker med gyldig session", passed, dashboard_response)

    # ------------------------------------------------------------
    # Test 3: Chat-history virker med gyldig session
    # ------------------------------------------------------------
    total_tests += 1

    history_response = requests.get(
        f"{BASE_URL}/session/chat-history",
        params={"session_id": session_id},
        timeout=30,
    )

    history_data = history_response.json() if history_response.ok else {}

    passed = (
        history_response.status_code == 200
        and "messages" in history_data
        and isinstance(history_data["messages"], list)
    )

    if passed:
        passed_tests += 1

    print_result("Test 3: Chat-history virker med gyldig session", passed, history_response)

    # ------------------------------------------------------------
    # Test 4: Chat med session gemmer historik
    # ------------------------------------------------------------
    total_tests += 1

    chat_response = requests.post(
        f"{BASE_URL}/chat",
        json={
            "message": "Hvad er min risikoprofil?",
            "session_id": session_id,
        },
        timeout=120,
    )

    passed = (
        chat_response.status_code == 200
        and "middel" in chat_response.json().get("reply", "").lower()
    )

    if passed:
        passed_tests += 1

    print_result("Test 4: Chat med session virker", passed, chat_response)

    # ------------------------------------------------------------
    # Test 5: Chat-history indeholder beskeder efter chat
    # ------------------------------------------------------------
    total_tests += 1

    updated_history_response = requests.get(
        f"{BASE_URL}/session/chat-history",
        params={"session_id": session_id},
        timeout=30,
    )

    updated_history_data = updated_history_response.json() if updated_history_response.ok else {}
    messages = updated_history_data.get("messages", [])

    passed = (
        updated_history_response.status_code == 200
        and len(messages) >= 2
    )

    if passed:
        passed_tests += 1

    print_result("Test 5: Chat-history gemmer beskeder", passed, updated_history_response)

    # ------------------------------------------------------------
    # Test 6: Refresh forlænger session
    # ------------------------------------------------------------
    total_tests += 1

    refresh_response = requests.post(
        f"{BASE_URL}/session/refresh",
        json={"session_id": session_id},
        timeout=30,
    )

    refresh_data = refresh_response.json() if refresh_response.ok else {}

    passed = (
        refresh_response.status_code == 200
        and "expires_at" in refresh_data
        and refresh_data.get("ttl_seconds") is not None
    )

    if passed:
        passed_tests += 1

    print_result("Test 6: Session refresh virker", passed, refresh_response)

    # ------------------------------------------------------------
    # Test 7: Logout virker
    # ------------------------------------------------------------
    total_tests += 1

    logout_response = requests.post(
        f"{BASE_URL}/logout",
        json={"session_id": session_id},
        timeout=30,
    )

    logout_data = logout_response.json() if logout_response.ok else {}

    passed = (
        logout_response.status_code == 200
        and logout_data.get("logged_out") is True
    )

    if passed:
        passed_tests += 1

    print_result("Test 7: Logout virker", passed, logout_response)

    # ------------------------------------------------------------
    # Test 8: Dashboard afvises efter logout
    # ------------------------------------------------------------
    total_tests += 1

    dashboard_after_logout_response = requests.get(
        f"{BASE_URL}/session/dashboard",
        params={"session_id": session_id},
        timeout=30,
    )

    passed = dashboard_after_logout_response.status_code == 401

    if passed:
        passed_tests += 1

    print_result(
        "Test 8: Dashboard afvises efter logout",
        passed,
        dashboard_after_logout_response,
    )

    # ------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------
    pass_rate = round((passed_tests / total_tests) * 100, 2)

    print("\n" + "=" * 80)
    print("SAMLET RESULTAT")
    print(f"Bestået: {passed_tests}/{total_tests}")
    print(f"Pass rate: {pass_rate}%")

    if passed_tests != total_tests:
        raise SystemExit(1)


if __name__ == "__main__":
    main()