const socket = io();

let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
  lineNumbers: true,
  mode: "text/x-c++src",
  theme: "dracula",
});

let username = prompt("Enter your name:") || "Anonymous";
document.getElementById("chat-box").innerHTML += `<div><strong>You joined as ${username}</strong></div>`;

let isRemoteUpdate = false;

editor.on("change", (instance, changeObj) => {
  if (isRemoteUpdate) return;
  const code = instance.getValue();
  socket.emit("code_change", code);
});

socket.on("code_update", (code) => {
  if (code !== editor.getValue()) {
    isRemoteUpdate = true;
    const cursor = editor.getCursor();
    editor.setValue(code);
    editor.setCursor(cursor);
    isRemoteUpdate = false;
  }
});

function runCode() {
  const code = editor.getValue();
  const languageId = document.getElementById("language").value;

  document.getElementById("output").textContent = "Running...";

  fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code: code, language_id: languageId })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("output").textContent = data.output;
    })
    .catch(err => {
      document.getElementById("output").textContent = "Error: " + err;
    });
}


// Chat logic
function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (message === "") return;

  socket.emit("chat_message", { user: username, message });
  input.value = "";
}

socket.on("chat_message", (data) => {
  const { user, message } = data;
  const chatBox = document.getElementById("chat-box");
  const formatted = `<div><strong>${user}:</strong> ${message}</div>`;
  chatBox.innerHTML += formatted;
  chatBox.scrollTop = chatBox.scrollHeight;
});
