(function () {
  const WARNING_SECONDS = 60;
  let countdownTimer = null;
  let countdownSeconds = WARNING_SECONDS;
  let warningVisible = false;

  function getSessionId() {
    return sessionStorage.getItem("session_id");
  }

  function clearSession() {
    sessionStorage.removeItem("session_id");
    sessionStorage.removeItem("session_expires_at");
    sessionStorage.removeItem("customer_name");
    sessionStorage.removeItem("customer_full_name");
    sessionStorage.removeItem("open_chat_after_login");
    sessionStorage.removeItem("chat_return_url");
    sessionStorage.removeItem("chat_widget_open");
    sessionStorage.removeItem("chat_messages");
    sessionStorage.removeItem("chat_login_completed");

    localStorage.removeItem("customer_id");
    localStorage.removeItem("session_id");
    localStorage.removeItem("customer_name");
    localStorage.removeItem("customer_full_name");
  }

  function redirectAfterLogout() {
    if (window.location.pathname.endsWith("logged-in.html")) {
      window.location.href = "login.html";
      return;
    }

    window.location.href = "index.html";
  }

  function logout(shouldCallBackend = true) {
    const sessionId = getSessionId();

    if (shouldCallBackend && sessionId) {
      fetch("http://127.0.0.1:8000/logout", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ session_id: sessionId })
      }).catch(() => {});
    }

    clearSession();
    redirectAfterLogout();
  }

  function ensureModal() {
    let modal = document.getElementById("sessionTimeoutModal");

    if (modal) {
      return modal;
    }

    modal = document.createElement("div");
    modal.id = "sessionTimeoutModal";
    modal.className = "session-timeout-overlay";
    modal.innerHTML = `
      <div class="session-timeout-dialog" role="dialog" aria-modal="true" aria-labelledby="sessionTimeoutTitle">
        <h2 id="sessionTimeoutTitle">Vil du forblive logget ind?</h2>
        <p>Af hensyn til dine pensionsoplysninger logger vi dig snart automatisk ud. Vælg, om du vil fortsætte sessionen.</p>
        <p class="session-timeout-countdown">Du logges ud om <strong id="sessionTimeoutCountdown">60</strong> sekunder.</p>
        <div class="session-timeout-actions">
          <button type="button" id="sessionStayLoggedIn" class="session-primary-btn">Forbliv logget ind</button>
          <button type="button" id="sessionLogoutNow" class="session-secondary-btn">Log ud nu</button>
        </div>
      </div>
    `;

    document.body.appendChild(modal);

    document.getElementById("sessionStayLoggedIn").addEventListener("click", stayLoggedIn);
    document.getElementById("sessionLogoutNow").addEventListener("click", () => logout(true));

    return modal;
  }

  function hideModal() {
    const modal = document.getElementById("sessionTimeoutModal");
    if (modal) {
      modal.classList.remove("open");
    }

    warningVisible = false;
    clearInterval(countdownTimer);
    countdownTimer = null;
  }

  function showModal() {
    if (warningVisible || !getSessionId()) {
      return;
    }

    const modal = ensureModal();
    const countdown = document.getElementById("sessionTimeoutCountdown");
    warningVisible = true;
    countdownSeconds = WARNING_SECONDS;
    countdown.textContent = countdownSeconds;
    modal.classList.add("open");

    clearInterval(countdownTimer);
    countdownTimer = setInterval(() => {
      countdownSeconds -= 1;
      countdown.textContent = Math.max(countdownSeconds, 0);

      if (countdownSeconds <= 0) {
        logout(true);
      }
    }, 1000);
  }

  async function stayLoggedIn() {
    const sessionId = getSessionId();
    if (!sessionId) {
      logout(false);
      return;
    }

    try {
      const response = await fetch("http://127.0.0.1:8000/session/refresh", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({ session_id: sessionId })
      });

      const data = await response.json();

      if (!response.ok) {
        logout(false);
        return;
      }

      sessionStorage.setItem("session_expires_at", data.expires_at);
      hideModal();
      scheduleWarning();
    } catch (error) {
      console.error("Kunne ikke forlænge session:", error);
      logout(false);
    }
  }

  function scheduleWarning() {
    const sessionId = getSessionId();
    const expiresAt = sessionStorage.getItem("session_expires_at");

    if (!sessionId || !expiresAt) {
      return;
    }

    const expiresAtMs = Date.parse(expiresAt);
    if (Number.isNaN(expiresAtMs)) {
      logout(false);
      return;
    }

    const warningAtMs = expiresAtMs - WARNING_SECONDS * 1000;
    const delay = warningAtMs - Date.now();

    clearTimeout(window.__sessionWarningTimer);

    if (delay <= 0) {
      showModal();
      return;
    }

    window.__sessionWarningTimer = setTimeout(showModal, delay);
  }

  window.PenSamSession = {
    getSessionId,
    clearSession,
    logout,
    scheduleWarning
  };

  document.addEventListener("DOMContentLoaded", scheduleWarning);
})();
