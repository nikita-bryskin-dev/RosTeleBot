function sendMessage() {
  const input = document.getElementById("message-input");
  const message = input.value.trim();
  if (message === "") return;

  const chatBox = document.getElementById("chat-box");
  chatBox.innerHTML += `<div><strong>Вы:</strong> ${message}</div>`;
  input.value = "";

  fetch("/chat", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ message: message })
  })
    .then(res => res.json())
    .then(data => {
      chatBox.innerHTML += `<div><strong>Бот:</strong> ${data.response}</div>`;
      // Можем сохранить ID, если нужно
      console.log("ID заявки:", data.request_id);
    });
}

function closeRequest() {
  const id = document.getElementById("close-request-id").value.trim();
  if (!id) return alert("Введите ID заявки");

  fetch("/update_status", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ id: id, status: "закрыто" })
  })
    .then(res => res.json())
    .then(data => alert(data.message));
}