let chatHistory = [];

let sessionId = window.PenSamSession ? window.PenSamSession.getSessionId() : sessionStorage.getItem("session_id");
if (!sessionId) {
  window.location.replace("login.html");
}

const customerName = sessionStorage.getItem("customer_name") || "kunde";
const customerFullName = sessionStorage.getItem("customer_full_name") || customerName;

const chatToggle = document.getElementById("chat-toggle");
const chatWidget = document.getElementById("chat-widget");
const chatClose = document.getElementById("chat-close");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const logoutBtn = document.querySelector(".login-btn");
const shouldKeepChatOpen = sessionStorage.getItem("chat_widget_open") === "true";
const suggestionButtons = document.querySelectorAll(".chat-suggestions button");
const loggedUserName = document.getElementById("loggedUserName");
const welcomeTitle = document.getElementById("welcomeTitle");
const chatWelcome = document.getElementById("chatWelcome");

loggedUserName.textContent = customerFullName;
welcomeTitle.textContent = `Hej ${customerName}`;
chatWelcome.textContent = `Hej ${customerName}! Du kan her stille generelle eller personlige spørgsmål om din pension.`;

if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    if (window.PenSamSession) {
      window.PenSamSession.logout(true);
    }
  });
}

chatToggle.addEventListener("click", () => {
  chatWidget.classList.add("open");
  sessionStorage.setItem("chat_widget_open", "true");
});

chatClose.addEventListener("click", () => {
  chatWidget.classList.remove("open");
  sessionStorage.setItem("chat_widget_open", "false");
});

if (shouldKeepChatOpen) {
  chatWidget.classList.add("open");
}

async function restoreAuthenticatedChatHistory() {
  if (!sessionId) {
    return;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/session/chat-history?session_id=${encodeURIComponent(sessionId)}`);
    if (!response.ok) {
      return;
    }

    const data = await response.json();
    const messages = data.messages || [];
    if (!messages.length) {
      return;
    }

    chatBox.innerHTML = "";
    messages.forEach((message) => {
      addMessageToChat(message.role === "user" ? "user" : "bot", message.content);
    });

    chatHistory = messages.map((message) => ({
      role: message.role === "user" ? "user" : "assistant",
      content: message.content
    }));
  } catch (error) {
    console.error("Kunne ikke hente gemt chathistorik:", error);
  }
}

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
});

suggestionButtons.forEach((button) => {
  button.addEventListener("click", () => {
    input.value = button.textContent;
    sendMessage();
  });
});

function createInfoRow(title, description, value) {
  const row = document.createElement("div");
  row.className = "info-row";

  const text = document.createElement("div");
  const strong = document.createElement("strong");
  const p = document.createElement("p");
  const span = document.createElement("span");

  strong.textContent = title;
  p.textContent = description;
  span.textContent = value;

  text.appendChild(strong);
  text.appendChild(p);
  row.appendChild(text);
  row.appendChild(span);

  return row;
}

function renderDashboard(data) {
  document.getElementById("totalBalance").textContent = data.total_balance;
  document.getElementById("accountSummary").textContent = data.account_summary;
  document.getElementById("monthlyContribution").textContent = data.monthly_contribution;
  document.getElementById("expectedPayout").textContent = data.expected_monthly_payout;
  document.getElementById("riskProfile").textContent = data.risk_profile;
  document.getElementById("returnLabel").textContent = `Afkast ${data.return.year}:`;
  document.getElementById("returnPercent").textContent = data.return.percent;
  document.getElementById("palTax").textContent = data.tax.pal_tax_total;
  document.getElementById("taxCode").textContent = data.tax.tax_code;
  document.getElementById("yearlyCostPercent").textContent = data.cost.yearly_cost_percent;
  document.getElementById("yearlyCostAmount").textContent = data.cost.yearly_cost_amount;

  const accountsList = document.getElementById("pensionAccountsList");
  accountsList.innerHTML = "";
  data.accounts.forEach((account) => {
    accountsList.appendChild(
      createInfoRow(
        `${account.pension_type} hos ${account.provider_name}`,
        `Policenummer: ${account.policy_number} · månedlig indbetaling ${account.monthly_contribution}`,
        account.current_balance
      )
    );
  });

  const insuranceList = document.getElementById("insuranceList");
  insuranceList.innerHTML = "";
  data.insurances.forEach((insurance) => {
    insuranceList.appendChild(
      createInfoRow(
        insurance.insurance_type,
        `Dækning: ${insurance.coverage_amount}`,
        insurance.active ? "Aktiv" : "Inaktiv"
      )
    );
  });
}

async function loadDashboard() {
  try {
    const response = await fetch(`http://127.0.0.1:8000/session/dashboard?session_id=${encodeURIComponent(sessionId)}`);
    if (response.status === 401) {
      if (window.PenSamSession) {
        window.PenSamSession.clearSession();
      }
      window.location.replace("login.html");
      return;
    }

    if (!response.ok) {
      throw new Error("Kunne ikke hente kundeoverblik");
    }

    const data = await response.json();
    renderDashboard(data);
  } catch (error) {
    console.error("Fejl ved kundeoverblik:", error);
    document.getElementById("accountSummary").textContent = "Tjek at backend og databasen kører.";
  }
}

async function sendMessage() {
  const message = input.value.trim();

  if (!message) return;

  addMessageToChat("user", message);
  input.value = "";

  try {
    const response = await fetch("http://127.0.0.1:8000/chat", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        message: message,
        session_id: sessionId,
        history: chatHistory.slice(-6)
      })
    });

    const data = await response.json();

    addMessageToChat("bot", data.reply);

    chatHistory.push({
      role: "user",
      content: message
    });

    chatHistory.push({
      role: "assistant",
      content: data.reply
    });

  } catch (error) {
    console.error("Fejl ved chat:", error);

    addMessageToChat(
      "bot",
      "Der opstod en fejl. Tjek at backend-serveren kører på http://127.0.0.1:8000"
    );
  }
}

function addMessageToChat(sender, text) {
  const messageElement = document.createElement("div");

  messageElement.classList.add("message");

  if (sender === "user") {
    messageElement.classList.add("user");
  } else {
    messageElement.classList.add("bot");
  }

  messageElement.textContent = text;

  chatBox.appendChild(messageElement);
  chatBox.scrollTop = chatBox.scrollHeight;
}

if (sessionId) {
  loadDashboard();
  restoreAuthenticatedChatHistory();
}
