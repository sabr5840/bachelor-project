let chatHistory = [];

let customerId = localStorage.getItem("customer_id");
if (!customerId) {
  customerId = "1";
  localStorage.setItem("customer_id", customerId);
  localStorage.setItem("customer_name", "Mette");
  localStorage.setItem("customer_full_name", "Mette Larsen");
}

const chatToggle = document.getElementById("chat-toggle");
const chatWidget = document.getElementById("chat-widget");
const chatClose = document.getElementById("chat-close");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
const logoutBtn = document.querySelector(".login-btn");
const shouldKeepChatOpen = sessionStorage.getItem("chat_widget_open") === "true";
const suggestionButtons = document.querySelectorAll(".chat-suggestions button");

if (logoutBtn) {
  logoutBtn.addEventListener("click", () => {
    localStorage.removeItem("customer_id");
    localStorage.removeItem("customer_name");
    localStorage.removeItem("customer_full_name");
    sessionStorage.removeItem("open_chat_after_login");
    sessionStorage.removeItem("chat_return_url");
    sessionStorage.removeItem("chat_widget_open");
    sessionStorage.removeItem("chat_messages");
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
        customer_id: customerId,
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
