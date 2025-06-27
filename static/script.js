const socket = io();
let editor = CodeMirror.fromTextArea(document.getElementById('editor'), {
  mode: "text/x-c++src",
  theme: "dracula",
  lineNumbers: true
});

document.getElementById("language").addEventListener("change", function () {
  const langMap = {
    "50": "text/x-csrc",
    "54": "text/x-c++src",
    "71": "python",
    "62": "text/x-java",
    "63": "javascript"
  };
  editor.setOption("mode", langMap[this.value]);
});

editor.on("change", () => {
  socket.emit("code_change", editor.getValue());
});

socket.on("code_update", (data) => {
  editor.setValue(data);
});

function runCode() {
  const code = editor.getValue();
  const lang = document.getElementById("language").value;
  fetch("/run", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ source_code: code, language_id: lang })
  })
    .then(res => res.json())
    .then(data => {
      document.getElementById("output").innerText = data.stdout || data.stderr || "No output";
    });
}

function sendMessage() {
  const msg = document.getElementById("chat-input").value.trim();
  if (msg) {
    socket.emit("chat_message", msg);
    document.getElementById("chat-input").value = "";
  }
}

socket.on("chat_message", msg => {
  const box = document.getElementById("chat-box");
  box.innerHTML += `<div>${msg}</div>`;
  box.scrollTop = box.scrollHeight;
});
