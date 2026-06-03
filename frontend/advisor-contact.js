const advisorBackButton = document.getElementById("advisorBackButton");

if (advisorBackButton) {
  advisorBackButton.addEventListener("click", () => {
    const returnUrl = sessionStorage.getItem("advisor_return_url");

    sessionStorage.setItem("chat_widget_open", "true");

    if (returnUrl) {
      window.location.href = returnUrl;
      return;
    }

    window.location.href = sessionStorage.getItem("session_id")
      ? "logged-in.html"
      : "index.html";
  });
}
