async function sendMessage() {
    const input = document.getElementById("user-input");
    const chatBox = document.getElementById("chat-box");

    const message = input.value;
    if (!message) return;

    // vis brugerens besked
    chatBox.innerHTML += `<div class="message user">${message}</div>`;

    input.value = "";

    // loading
    chatBox.innerHTML += `<div class="message bot">AI tænker...eller backend slukket</div>`;

    // kald backend
    const response = await fetch("http://127.0.0.1:8000/chat", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ message })
    });

    const data = await response.json();

    // fjern loading (hacky men fint til nu)
    chatBox.innerHTML = chatBox.innerHTML.replace("AI tænker...eller backend slukket", "");

    // vis svar
    chatBox.innerHTML += `<div class="message bot">${data.reply}</div>`;
}