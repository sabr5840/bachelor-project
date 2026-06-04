const chatToggle = document.getElementById("chat-toggle");
const chatWidget = document.getElementById("chat-widget");
const chatClose = document.getElementById("chat-close");
const userInput = document.getElementById("user-input");
const chatBox = document.getElementById("chat-box");
let chatSuggestions = document.getElementById("chatSuggestions") || document.querySelector(".chat-suggestions");
let chatHistory = [];
const sessionId = window.PenSamSession ? window.PenSamSession.getSessionId() : sessionStorage.getItem("session_id");
const customerName = sessionStorage.getItem("customer_name");
const customerFullName = sessionStorage.getItem("customer_full_name") || customerName;
const shouldOpenChat = sessionStorage.getItem("open_chat_after_login") === "true";
const shouldKeepChatOpen = sessionStorage.getItem("chat_widget_open") === "true";
const shouldShowLoginCompletedMessage = sessionStorage.getItem("chat_login_completed") === "true";
const shouldShowLoggedOutNotice = sessionStorage.getItem("chat_logged_out_notice") === "true";
const pendingPersonalQuestion = sessionStorage.getItem("pending_personal_question");
const topbarRight = document.querySelector(".topbar-right");
const isLoginPage = document.body.classList.contains("login-body");
const isAdvisorContactPage = window.location.pathname.endsWith("advisor-contact.html");
const shouldShowAdvisorContactNotice = sessionStorage.getItem("chat_contact_advisor_notice") === "true";

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

async function restoreAuthenticatedChatHistory() {
  if (!sessionId || !chatBox) {
    return false;
  }

  try {
    const response = await fetch(`http://127.0.0.1:8000/session/chat-history?session_id=${encodeURIComponent(sessionId)}`);
    if (!response.ok) {
      return false;
    }

    const data = await response.json();
    const messages = data.messages || [];
    if (!messages.length) {
      return false;
    }

    chatBox.innerHTML = "";
    if (shouldShowLoginCompletedMessage) {
      appendMessage(
        `Du er logget ind igen, ${customerName}. Din seneste samtale er gendannet, så du kan fortsætte herfra.`,
        "bot",
        false
      );
    }

    messages.forEach((message) => {
      appendMessage(message.content, message.role === "user" ? "user" : "bot", false);
    });

    chatHistory = messages.map((message) => ({
      role: message.role === "user" ? "user" : "assistant",
      content: message.content
    }));

    return true;
  } catch (error) {
    console.error("Kunne ikke hente gemt chathistorik:", error);
    return false;
  }
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

function isLoginRequiredReply(reply) {
  return (
    typeof reply === "string" &&
    reply.includes("kræver") &&
    reply.toLowerCase().includes("log ind")
  );
}

function resumePendingPersonalQuestion() {
  if (!sessionId || !pendingPersonalQuestion || !chatBox || isLoginPage) {
    return;
  }

  sessionStorage.removeItem("pending_personal_question");
  appendMessage(
    `Du spurgte: "${pendingPersonalQuestion}". Nu hvor du er logget ind, fortsætter jeg herfra.`,
    "bot"
  );

  if (userInput) {
    userInput.value = pendingPersonalQuestion;
    sendMessage();
  }
}

function removeChatActionChips() {
  document.querySelectorAll(".chat-action-chips").forEach((element) => element.remove());
}

function saveChatActionSuggestions(suggestions = []) {
  if (!Array.isArray(suggestions) || suggestions.length === 0) {
    sessionStorage.removeItem("chat_action_suggestions");
    return;
  }

  sessionStorage.setItem("chat_action_suggestions", JSON.stringify(suggestions));
}

function getSavedChatActionSuggestions() {
  try {
    return JSON.parse(sessionStorage.getItem("chat_action_suggestions")) || [];
  } catch (error) {
    return [];
  }
}

function showContactAdvisorMessage() {
  sessionStorage.setItem("chat_contact_advisor_notice", "true");
  sessionStorage.setItem("chat_widget_open", "false");
  sessionStorage.setItem("advisor_return_url", window.location.href);
  window.location.href = "advisor-contact.html";
}

function renderChatActionChips(suggestions = []) {
  if (!chatBox || !Array.isArray(suggestions) || suggestions.length === 0) {
    saveChatActionSuggestions([]);
    return;
  }

  removeChatActionChips();
  saveChatActionSuggestions(suggestions);

  const chips = document.createElement("div");
  chips.className = "chat-action-chips";
  chips.setAttribute("aria-label", "Forslag til næste spørgsmål");

  const hint = document.createElement("p");
  hint.className = "chat-action-hint";
  hint.textContent = "Vælg et forslag, eller skriv dit eget spørgsmål.";
  chips.appendChild(hint);

  suggestions.forEach((suggestion) => {
    const button = document.createElement("button");
    button.type = "button";
    button.textContent = suggestion.label;

    button.addEventListener("click", () => {
      removeChatActionChips();

      if (suggestion.action === "contact_advisor") {
        showContactAdvisorMessage();
        return;
      }

      sessionStorage.removeItem("chat_action_suggestions");

      if (userInput && suggestion.message) {
        userInput.value = suggestion.message;
        sendMessage();
      }
    });

    chips.appendChild(button);
  });

  chatBox.appendChild(chips);
  chatBox.scrollTop = chatBox.scrollHeight;
}

if (sessionId && customerName && topbarRight) {
  const loginLink = topbarRight.querySelector(".login-btn");
  const loggedUser = document.createElement("a");

  loggedUser.classList.add("logged-user");
  loggedUser.textContent = customerFullName;
  loggedUser.href = "logged-in.html";
  loggedUser.setAttribute("aria-label", "Gå til din profilside");

  if (loginLink) {
    loginLink.textContent = "Log ud";
    loginLink.href = "index.html";
    loginLink.addEventListener("click", () => {
      if (window.PenSamSession) {
        window.PenSamSession.logout(true);
      }
    });

    topbarRight.insertBefore(loggedUser, loginLink);
  }
}

const restoredChat = restoreChatMessages();

if (!sessionId && shouldShowLoggedOutNotice && chatBox) {
  chatBox.innerHTML = "";
  appendMessage(
    "Du er nu logget ud. Af hensyn til dine pensionsoplysninger er samtalen skjult. Hvis du logger ind igen inden for kort tid, kan du fortsætte samtalen.",
    "bot",
    false
  );
  sessionStorage.removeItem("chat_logged_out_notice");
}

if (
  sessionId &&
  customerName &&
  chatBox &&
  !restoredChat &&
  !shouldShowLoginCompletedMessage
) {
  chatBox.innerHTML = "";
  appendMessage(
    `hej ${customerName}! Du kan her stille generelle eller personlige spørgsmål om din pension`,
    "bot",
    false
  );

  if (userInput) {
    userInput.placeholder = "Spørg om din pension";
  }
}

if (isAdvisorContactPage && shouldShowAdvisorContactNotice && chatBox) {
  appendMessage(
    "Du har valgt Kontakt rådgiver. Du er nu på kontaktsiden med rådgiverens oplysninger.",
    "bot",
    false
  );
  sessionStorage.removeItem("chat_contact_advisor_notice");
}

if (sessionId && customerName && shouldShowLoginCompletedMessage && chatBox && !isLoginPage) {
  chatBox.innerHTML = "";
  appendMessage(
    `Du er nu logget ind, ${customerName}! Jeg kan stadig svare på generelle spørgsmål, og du kan også spørge om dine egne pensionsoplysninger.`,
    "bot"
  );
  sessionStorage.removeItem("chat_login_completed");
}

if (sessionId && customerName && chatBox) {
  const welcomeMessage = chatBox.querySelector(".chat-welcome");
  if (welcomeMessage) {
    welcomeMessage.remove();
  }

  if (userInput) {
    userInput.placeholder = "Spørg om din pension";
  }
}

setChatSuggestions(Boolean(sessionId && customerName));

if (
    sessionId &&
    !window.location.pathname.includes("logged-in.html")
) {
    restoreAuthenticatedChatHistory();
}

if (sessionId && pendingPersonalQuestion) {
  setTimeout(resumePendingPersonalQuestion, 300);
}

if (chatToggle && chatWidget) {
  chatToggle.addEventListener("click", () => {
    chatWidget.classList.toggle("open");
    sessionStorage.setItem("chat_widget_open", chatWidget.classList.contains("open") ? "true" : "false");
    sessionStorage.setItem("chat_return_url", window.location.href);
  });
}

if ((shouldOpenChat || (shouldKeepChatOpen && !isAdvisorContactPage)) && chatWidget) {
  chatWidget.classList.add("open");
  sessionStorage.setItem("chat_widget_open", "true");
  sessionStorage.removeItem("open_chat_after_login");
} else if (isAdvisorContactPage && chatWidget) {
  chatWidget.classList.remove("open");
  sessionStorage.setItem("chat_widget_open", "false");
}

if (chatWidget && chatWidget.classList.contains("open")) {
  setTimeout(() => renderChatActionChips(getSavedChatActionSuggestions()), 300);
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
        session_id: sessionId,
        history: chatHistory.slice(-6)
      })
    });

    if (!response.ok) {
      throw new Error("Backend returnerede en fejl");
    }

    const data = await response.json();

    loadingElement.remove();
    removeChatActionChips();
    appendMessage(data.reply, "bot");
    renderChatActionChips(data.suggestions);

    if (!sessionId && isLoginRequiredReply(data.reply)) {
      sessionStorage.setItem("pending_personal_question", message);
      sessionStorage.setItem("chat_return_url", window.location.href);
      sessionStorage.setItem("chat_widget_open", "true");
    }

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
  messageDiv.innerHTML = marked.parse(
      text || "",
      {
          breaks: true,
          gfm: true
      }
  
  );

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
