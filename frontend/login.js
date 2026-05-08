const openBtn = document.getElementById("openMitidBtn");
const startView = document.getElementById("mitid-start");
const qrView = document.getElementById("mitid-qr");
const loginButton = document.getElementById("loginButton");
const statusPill = document.getElementById("mitidStatusPill");
const mitidSessionIdElement = document.getElementById("mitidSessionId");
const countdown = document.getElementById("qrCountdown");
const timerProgress = document.getElementById("timerProgress");
const fakeQr = document.getElementById("fakeQr");
const mitidUserIdInput = document.getElementById("mitidUserId");
const mitidUserHelp = document.getElementById("mitidUserHelp");
const mitidUserError = document.getElementById("mitidUserError");
const stepItems = document.querySelectorAll("#mitidSteps li");
const returnTo = new URLSearchParams(window.location.search).get("returnTo");
let countdownTimer;
let statusTimers = [];
let currentCountdown = 49;
let selectedCustomer = null;
let resolvedUserId = "";

const mitidStatuses = [
    { delay: 500, step: 0, label: "Opretter login-session" },
    { delay: 1500, step: 1, label: "QR-kode klar" },
    { delay: 3000, step: 2, label: "Venter på MitID-app" },
    { delay: 5200, step: 3, label: "QR-kode scannet" },
    { delay: 7200, step: 4, label: "Identitet bekræftet", complete: true }
];

function getSafeReturnTo() {
    if (!returnTo) {
        return null;
    }

    const returnUrl = new URL(returnTo, window.location.href);
    if (returnUrl.origin !== window.location.origin) {
        return null;
    }

    return returnUrl.href;
}

function createSessionId() {
    return `Session: MID-${Math.floor(100000 + Math.random() * 900000)}`;
}

function validateMitidUserIdFormat(userId) {
    if (userId !== userId.trim()) {
        return "Bruger-ID må ikke starte eller slutte med mellemrum.";
    }

    if (userId.length < 5 || userId.length > 48) {
        return "Bruger-ID skal være mellem 5 og 48 tegn.";
    }

    if (/^\d{10}$/.test(userId)) {
        return "Bruger-ID må ikke bestå af 10 tal.";
    }

    if (/^\d{6}-?\d{4}$/.test(userId)) {
        return "Bruger-ID må ikke være dit CPR-nummer.";
    }

    if (!/^[A-Za-zÆØÅæøå0-9 {}!#$ ^,*()_+\-=:;?.@]+$/.test(userId)) {
        return "Bruger-ID indeholder tegn, som ikke er tilladt.";
    }

    return "";
}

function setMitidError(message) {
    mitidUserError.textContent = message;
    mitidUserIdInput.classList.toggle("invalid", Boolean(message));
}

async function resolveMitidUser() {
    const userId = mitidUserIdInput.value;
    const validationError = validateMitidUserIdFormat(userId);

    if (validationError) {
        setMitidError(validationError);
        return null;
    }

    try {
        openBtn.disabled = true;
        openBtn.textContent = "Kontrollerer bruger-ID";

        const response = await fetch("http://127.0.0.1:8000/mitid/resolve-user", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ user_id: userId })
        });

        const data = await response.json();

        if (!response.ok) {
            setMitidError(data.detail || "Bruger-ID kunne ikke bruges.");
            return null;
        }

        setMitidError("");
        resolvedUserId = userId;
        return data.customer;
    } catch (error) {
        console.error("Fejl ved MitID-opslag:", error);
        setMitidError("Tjek at backend og databasen kører, og prøv igen.");
        return null;
    } finally {
        openBtn.disabled = false;
        openBtn.textContent = "Åbn MitID";
    }
}

function updateStep(activeStep) {
    stepItems.forEach((item, index) => {
        item.classList.toggle("active", index === activeStep);
        item.classList.toggle("done", index < activeStep);
    });
}

function updateCountdown() {
    currentCountdown -= 1;
    countdown.textContent = currentCountdown;
    timerProgress.style.width = `${(currentCountdown / 49) * 100}%`;

    if (currentCountdown <= 0) {
        clearInterval(countdownTimer);
        currentCountdown = 49;
        countdown.textContent = currentCountdown;
        fakeQr.classList.toggle("refreshed");
        timerProgress.style.width = "100%";
        countdownTimer = setInterval(updateCountdown, 1000);
    }
}

function startMitidSimulation() {
    currentCountdown = 49;
    mitidSessionIdElement.textContent = createSessionId();
    countdown.textContent = currentCountdown;
    timerProgress.style.width = "100%";
    loginButton.disabled = true;
    statusPill.classList.remove("verified");
    updateStep(0);

    clearInterval(countdownTimer);
    statusTimers.forEach((timer) => clearTimeout(timer));
    statusTimers = [];

    countdownTimer = setInterval(updateCountdown, 1000);

    mitidStatuses.forEach((status) => {
        const timer = setTimeout(() => {
            statusPill.textContent = status.label;
            updateStep(status.step);

            if (status.complete) {
                statusPill.classList.add("verified");
                loginButton.disabled = false;
                clearInterval(countdownTimer);
            }
        }, status.delay);

        statusTimers.push(timer);
    });
}

openBtn.addEventListener("click", async () => {
    selectedCustomer = await resolveMitidUser();
    if (!selectedCustomer) {
        return;
    }

    mitidUserHelp.textContent = `Logger ind som ${selectedCustomer.full_name}.`;
    startView.style.display = "none";
    qrView.style.display = "block";
    startMitidSimulation();
});

mitidUserIdInput.addEventListener("input", () => {
    setMitidError("");
});

mitidUserIdInput.addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        openBtn.click();
    }
});

// Når login godkendes
loginButton.addEventListener("click", async () => {
    if (loginButton.disabled) {
        return;
    }

    try {
        loginButton.disabled = true;
        loginButton.textContent = "Logger ind";

        const response = await fetch("http://127.0.0.1:8000/mitid/complete-login", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ user_id: resolvedUserId })
        });

        const data = await response.json();

        if (!response.ok) {
            setMitidError(data.detail || "Login kunne ikke gennemføres.");
            startView.style.display = "block";
            qrView.style.display = "none";
            return;
        }

        selectedCustomer = data.customer;
        if (window.PenSamSession) {
            window.PenSamSession.clearSession();
        }
        sessionStorage.setItem("session_id", data.session_id);
        sessionStorage.setItem("session_expires_at", data.expires_at);
        sessionStorage.setItem("customer_name", selectedCustomer.first_name);
        sessionStorage.setItem("customer_full_name", selectedCustomer.full_name);
        if (window.PenSamSession) {
            window.PenSamSession.scheduleWarning();
        }
    } catch (error) {
        console.error("Fejl ved login:", error);
        setMitidError("Tjek at backend og databasen kører, og prøv igen.");
        startView.style.display = "block";
        qrView.style.display = "none";
        return;
    } finally {
        loginButton.textContent = "Godkend login";
    }

    sessionStorage.setItem("chat_login_completed", "true");
    const safeReturnTo = getSafeReturnTo();

    if (safeReturnTo) {
        sessionStorage.setItem("open_chat_after_login", "true");
        window.location.href = safeReturnTo;
        return;
    }

    window.location.href = "logged-in.html";
});

// Cancel
document.getElementById("cancelButton").addEventListener("click", () => {
    window.location.href = "index.html";
});
