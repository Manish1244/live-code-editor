const socket = io();
let editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
  mode: "python",
  theme: "dracula",
  lineNumbers: true,
  tabSize: 2,
  autoCloseBrackets: true
});

let username = prompt("Enter your name:");
if (!username) username = "Anonymous";
socket.emit("join", { name: username });

// Language selection
document.getElementById("language").addEventListener("change", (e) => {
  const modeMap = {
    50: "text/x-csrc",
    54: "text/x-c++src",
    71: "python",
    62: "text/x-java",
    63: "javascript"
  };
  editor.setOption("mode", modeMap[e.target.value]);
});

// Code synchronization
let isTyping = false;
editor.on("change", (instance, changeObj) => {
  if (isTyping) return;
  const code = instance.getValue();
  socket.emit("code_change", { code });
});

// Receiving code changes
socket.on("code_update", (data) => {
  isTyping = true;
  const cursor = editor.getCursor();
  editor.setValue(data.code);
  editor.setCursor(cursor); // Maintain cursor position
  isTyping = false;
});

// Send message
function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (message !== "") {
    socket.emit("send_message", { message });
    input.value = "";
  }
}

// Display chat messages
socket.on("chat_message", (data) => {
  const box = document.getElementById("chat-box");
  const line = document.createElement("div");
  line.innerHTML = `<strong>${data.name}:</strong> ${data.message}`;
  box.appendChild(line);
  box.scrollTop = box.scrollHeight;
});

// Run code
function runCode() {
  const code = editor.getValue();
  const langId = document.getElementById("language").value;

  document.getElementById("output").innerText = "Running...";

  fetch("/run", {
    method: "POST",
    headers: {
      "Content-Type": "application/json"
    },
    body: JSON.stringify({ code: code, language: langId })
  })
    .then((res) => res.json())
    .then((data) => {
      document.getElementById("output").innerText = data.output;
    })
    .catch((err) => {
      document.getElementById("output").innerText = "Execution error.";
      console.error(err);
    });
}
