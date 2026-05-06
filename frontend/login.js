const openBtn = document.getElementById("openMitidBtn");
const startView = document.getElementById("mitid-start");
const qrView = document.getElementById("mitid-qr");
const loginButton = document.getElementById("loginButton");
const statusPill = document.getElementById("mitidStatusPill");
const sessionId = document.getElementById("mitidSessionId");
const countdown = document.getElementById("qrCountdown");
const timerProgress = document.getElementById("timerProgress");
const fakeQr = document.getElementById("fakeQr");
const stepItems = document.querySelectorAll("#mitidSteps li");
const returnTo = new URLSearchParams(window.location.search).get("returnTo");
let countdownTimer;
let statusTimers = [];
let currentCountdown = 49;

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
    sessionId.textContent = createSessionId();
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

openBtn.addEventListener("click", () => {
    startView.style.display = "none";
    qrView.style.display = "block";
    startMitidSimulation();
});

// Når login godkendes
loginButton.addEventListener("click", () => {
    if (loginButton.disabled) {
        return;
    }

    localStorage.setItem("customer_id", "1");
    localStorage.setItem("customer_name", "Mette");
    localStorage.setItem("customer_full_name", "Mette Larsen");
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
