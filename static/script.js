async function sendMessage() {
    const input = document.getElementById("message-input");
    const message = input.value.trim();
    if (!message) return;
  
    const chatBox = document.getElementById("chat-box");
    chatBox.innerHTML += `<div class="user-msg"><strong>Вы:</strong> ${message}</div>`;
    input.value = "";
  
    const res = await fetch("/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message })
    });
  
    const data = await res.json();
    chatBox.innerHTML += `<div class="bot-msg"><strong>Бот:</strong> ${data.response}</div>`;
    chatBox.scrollTop = chatBox.scrollHeight;
  }
  