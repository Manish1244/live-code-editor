const socket = io();
const editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
  lineNumbers: true,
  theme: "dracula",
  mode: "text/x-csrc",
});

const languageModeMap = {
  "50": "text/x-csrc",         // C
  "54": "text/x-c++src",       // C++
  "71": "python",              // Python
  "62": "text/x-java",         // Java
  "63": "javascript",          // JavaScript
};

// Update editor mode when language changes
document.getElementById("language").addEventListener("change", function () {
  const langId = this.value;
  editor.setOption("mode", languageModeMap[langId]);
});

let isRemoteChange = false;

// Send code changes to server
editor.on("change", () => {
  if (!isRemoteChange) {
    socket.emit("code_change", { code: editor.getValue() });
  }
});

// Apply remote code update
socket.on("code_update", (data) => {
  isRemoteChange = true;
  editor.setValue(data.code);
  isRemoteChange = false;
});

// Handle sending chat message
function sendMessage() {
  const msg = document.getElementById("chat-input").value;
  if (msg.trim()) {
    socket.emit("chat_message", msg);
    document.getElementById("chat-input").value = "";
  }
}

// Append chat message
socket.on("new_message", (msg) => {
  const box = document.getElementById("chat-box");
  const el = document.createElement("div");
  el.textContent = msg;
  box.appendChild(el);
  box.scrollTop = box.scrollHeight;
});

// Run code
async function runCode() {
  const code = editor.getValue();
  const languageId = document.getElementById("language").value;

  document.getElementById("output").textContent = "Running...";

  const res = await fetch("https://judge0-ce.p.rapidapi.com/submissions", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "X-RapidAPI-Key": "3598f885a0mshcffa68d4a63d140p1acd22jsn54524acc6c9e",
      "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
    },
    body: JSON.stringify({
      language_id: languageId,
      source_code: code,
    }),
  });

  const { token } = await res.json();

  let result;
  while (true) {
    const check = await fetch(`https://judge0-ce.p.rapidapi.com/submissions/${token}`, {
      method: "GET",
      headers: {
        "X-RapidAPI-Key": "3598f885a0mshcffa68d4a63d140p1acd22jsn54524acc6c9e",
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
      },
    });

    result = await check.json();
    if (result.status.id >= 3) break;
  }

  const outputBox = document.getElementById("output");
  outputBox.textContent = result.stdout || result.stderr || "No Output";
}
