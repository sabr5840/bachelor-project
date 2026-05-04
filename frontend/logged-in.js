let chatHistory = [];

const chatToggle = document.getElementById("chat-toggle");
const chatWidget = document.getElementById("chat-widget");
const chatClose = document.getElementById("chat-close");
const input = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");

chatToggle.addEventListener("click", () => {
  chatWidget.classList.add("open");
});

chatClose.addEventListener("click", () => {
  chatWidget.classList.remove("open");
});

input.addEventListener("keydown", (event) => {
  if (event.key === "Enter") {
    sendMessage();
  }
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
        customer_id: 1,
        history: chatHistory
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