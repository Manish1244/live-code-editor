const socket = io();
const name = prompt("Enter your name:") || "Anonymous";
socket.emit("join", { name });

const editor = CodeMirror(document.getElementById("editor"), {
  mode: "python",
  theme: "dracula",
  lineNumbers: true
});

editor.on("change", () => {
  const code = editor.getValue();
  socket.emit("code_change", { code });
});

socket.on("code_update", (data) => {
  const cursor = editor.getCursor();
  editor.setValue(data.code);
  editor.setCursor(cursor);
});

function runCode() {
  const code = editor.getValue();
  const language = document.getElementById("language").value;

  fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code, language })
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById("output").textContent = data.output;
  });
}

function sendMessage() {
  const input = document.getElementById("message");
  const msg = input.value.trim();
  if (msg) {
    socket.emit("send_message", { message: msg });
    input.value = "";
  }
}

socket.on("chat_message", (data) => {
  const chat = document.getElementById("chat");
  const div = document.createElement("div");
  div.innerHTML = `<b>${data.name}:</b> ${data.message}`;
  chat.appendChild(div);
  chat.scrollTop = chat.scrollHeight;
});
