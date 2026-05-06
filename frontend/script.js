const chatToggle = document.getElementById("chat-toggle");
const chatWidget = document.getElementById("chat-widget");
const chatClose = document.getElementById("chat-close");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
let chatSuggestions = document.getElementById("chatSuggestions") || document.querySelector(".chat-suggestions");
let chatHistory = [];
const customerId = localStorage.getItem("customer_id");
const customerName = localStorage.getItem("customer_name");
const customerFullName = localStorage.getItem("customer_full_name") || customerName;
const shouldOpenChat = sessionStorage.getItem("open_chat_after_login") === "true";
const shouldKeepChatOpen = sessionStorage.getItem("chat_widget_open") === "true";
const shouldShowLoginCompletedMessage = sessionStorage.getItem("chat_login_completed") === "true";
const topbarRight = document.querySelector(".topbar-right");
const isLoginPage = document.body.classList.contains("login-body");

function getStoredChatMessages() {
  try {
    return JSON.parse(sessionStorage.getItem("chat_messages")) || [];
  } catch (error) {
    return [];
  }
}

function saveChatMessage(sender, text) {
  const storedMessages = getStoredChatMessages();
  storedMessages.push({ sender, text });
  sessionStorage.setItem("chat_messages", JSON.stringify(storedMessages.slice(-12)));
}

function restoreChatMessages() {
  const storedMessages = getStoredChatMessages();

  if (!storedMessages.length || !chatBox) {
    return false;
  }

  chatBox.innerHTML = "";

  storedMessages.forEach((message) => {
    appendMessage(message.text, message.sender, false);
  });

  chatHistory = storedMessages.map((message) => ({
    role: message.sender === "user" ? "user" : "assistant",
    content: message.text
  }));

  return true;
}

function getChatSuggestionsContainer() {
  if (!chatBox) {
    return null;
  }

  if (!chatSuggestions || !chatSuggestions.isConnected) {
    chatSuggestions = document.createElement("div");
    chatSuggestions.id = "chatSuggestions";
    chatSuggestions.classList.add("chat-suggestions");
    chatSuggestions.setAttribute("aria-label", "Forslag til spørgsmål");
    chatBox.appendChild(chatSuggestions);
  }

  return chatSuggestions;
}

function setChatSuggestions(isLoggedIn) {
  const suggestionsContainer = getChatSuggestionsContainer();

  if (!suggestionsContainer) {
    return;
  }

  const suggestions = isLoggedIn
    ? [
        "Hvor meget har jeg sparet op til pension?",
        "Hvad får jeg udbetalt om måneden som pensionist?",
        "Hvilke pensionsordninger har jeg?",
        "Hvad er ratepension?",
        "Hvad betyder livrente?"
      ]
    : [
        "Hvad er ratepension?",
        "Hvornår kan pension udbetales?",
        "Hvad betyder livrente?"
      ];

  suggestionsContainer.innerHTML = "";

  suggestions.forEach((suggestion) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = suggestion;
    button.addEventListener("click", () => {
      if (!userInput) return;

      userInput.value = suggestion;
      sendMessage();
    });

    suggestionsContainer.appendChild(button);
  });
}

if (customerId && customerName && topbarRight) {
  const loginLink = topbarRight.querySelector(".login-btn");
  const loggedUser = document.createElement("span");

  loggedUser.classList.add("logged-user");
  loggedUser.textContent = customerFullName;

  if (loginLink) {
    loginLink.textContent = "Log ud";
    loginLink.href = "index.html";
    loginLink.addEventListener("click", () => {
      localStorage.removeItem("customer_id");
      localStorage.removeItem("customer_name");
      localStorage.removeItem("customer_full_name");
      sessionStorage.removeItem("open_chat_after_login");
      sessionStorage.removeItem("chat_return_url");
      sessionStorage.removeItem("chat_widget_open");
      sessionStorage.removeItem("chat_messages");
      sessionStorage.removeItem("chat_login_completed");
    });

    topbarRight.insertBefore(loggedUser, loginLink);
  }
}

const restoredChat = restoreChatMessages();

if (
  customerId &&
  customerName &&
  chatBox &&
  !restoredChat &&
  !shouldShowLoginCompletedMessage
) {
  chatBox.innerHTML = "";
  appendMessage(
    `hej ${customerName}! Du kan her stillede generelle eller personlige spørgsmål om din pension`,
    "bot",
    false
  );

  if (userInput) {
    userInput.placeholder = "Spørg om din pension";
  }
}

if (customerId && customerName && shouldShowLoginCompletedMessage && chatBox && !isLoginPage) {
  chatBox.innerHTML = "";
  appendMessage(
    `Du er nu logget ind, ${customerName}! Jeg kan stadig svare på generelle spørgsmål, og du kan også spørge om dine egne pensionsoplysninger.`,
    "bot"
  );
  sessionStorage.removeItem("chat_login_completed");
}

if (customerId && customerName && chatBox) {
  const welcomeMessage = chatBox.querySelector(".chat-welcome");
  if (welcomeMessage) {
    welcomeMessage.remove();
  }

  if (userInput) {
    userInput.placeholder = "Spørg om din pension";
  }
}

setChatSuggestions(Boolean(customerId && customerName));

if (chatToggle && chatWidget) {
  chatToggle.addEventListener("click", () => {
    chatWidget.classList.toggle("open");
    sessionStorage.setItem("chat_widget_open", chatWidget.classList.contains("open") ? "true" : "false");
    sessionStorage.setItem("chat_return_url", window.location.href);
  });
}

if ((shouldOpenChat || (shouldKeepChatOpen && !isLoginPage)) && chatWidget) {
  chatWidget.classList.add("open");
  sessionStorage.setItem("chat_widget_open", "true");
  sessionStorage.removeItem("open_chat_after_login");
} else if (isLoginPage) {
  sessionStorage.setItem("chat_widget_open", "false");
}

if (chatClose && chatWidget) {
  chatClose.addEventListener("click", () => {
    chatWidget.classList.remove("open");
    sessionStorage.setItem("chat_widget_open", "false");
  });
}

const loginBtn = document.getElementById("loginBtn");

if (loginBtn) {
  loginBtn.addEventListener("click", () => {
    const returnUrl = sessionStorage.getItem("chat_return_url") || window.location.href;
    sessionStorage.setItem("chat_widget_open", "false");
    sessionStorage.setItem("chat_return_url", returnUrl);
    window.location.href = `login.html?returnTo=${encodeURIComponent(returnUrl)}`;
  });
}

async function sendMessage() {
  const input = document.getElementById("user-input");

  const message = input.value.trim();
  if (!message) return;

  appendMessage(message, "user");
  input.value = "";

  chatHistory.push({
    role: "user",
    content: message
  });

  const loadingElement = appendMessage("Genererer svar...", "bot", false);

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

    if (!response.ok) {
      throw new Error("Backend returnerede en fejl");
    }

    const data = await response.json();

    loadingElement.remove();
    appendMessage(data.reply, "bot");

    chatHistory.push({
      role: "assistant",
      content: data.reply
    });

  } catch (error) {
    loadingElement.remove();
    appendMessage("Der opstod en fejl ved kontakt til backend eller AI.", "bot");
    console.error(error);
  }
}

function appendMessage(text, sender, shouldPersist = true) {
  const chatBox = document.getElementById("chat-box");
  const messageDiv = document.createElement("div");

  messageDiv.classList.add("message", sender);
  messageDiv.textContent = text;

  chatBox.appendChild(messageDiv);
  chatBox.scrollTop = chatBox.scrollHeight;

  if (shouldPersist) {
    saveChatMessage(sender, text);
  }

  return messageDiv;
}

if (userInput) {
  userInput.addEventListener("keydown", function (event) {
    if (event.key === "Enter") {
      sendMessage();
    }
  });
}
