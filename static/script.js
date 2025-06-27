const socket = io();
let username = prompt("Enter your name:") || "Anonymous";

// CodeMirror setup
const editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
  mode: "text/x-c++src",
  theme: "dracula",
  lineNumbers: true,
  indentUnit: 4,
  tabSize: 4,
});

// Handle real-time code sync
editor.on("change", () => {
  const code = editor.getValue();
  socket.emit("code_change", { code });
});

socket.on("code_update", (data) => {
  const currentCode = editor.getValue();
  if (currentCode !== data.code) {
    const cursor = editor.getCursor();
    editor.setValue(data.code);
    editor.setCursor(cursor);
  }
});

// Handle chat sending
function sendMessage() {
  const input = document.getElementById("chat-input");
  const message = input.value.trim();
  if (message !== "") {
    socket.emit("chat_message", { user: username, message });
    input.value = "";
  }
}

// Handle chat receiving
socket.on("chat_update", (data) => {
  const chatBox = document.getElementById("chat-box");
  const message = document.createElement("div");
  message.innerText = `${data.user}: ${data.message}`;
  chatBox.appendChild(message);
  chatBox.scrollTop = chatBox.scrollHeight;
});

// Handle Judge0 code execution
async function runCode() {
  const outputBox = document.getElementById("output");
  outputBox.textContent = "Running code...";

  const code = editor.getValue();
  const languageId = document.getElementById("language").value;

  try {
    const response = await fetch("https://judge0-ce.p.rapidapi.com/submissions?base64_encoded=false&wait=true", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-RapidAPI-Host": "judge0-ce.p.rapidapi.com",
        "X-RapidAPI-Key": "3598f885a0mshcffa68d4a63d140p1acd22jsn54524acc6c9e" // Replace with your actual RapidAPI key
      },
      body: JSON.stringify({
        source_code: code,
        language_id: languageId,
      }),
    });

    const result = await response.json();

    if (result.stdout) {
      outputBox.textContent = result.stdout;
    } else if (result.stderr) {
      outputBox.textContent = "Error:\n" + result.stderr;
    } else if (result.compile_output) {
      outputBox.textContent = "Compilation Error:\n" + result.compile_output;
    } else {
      outputBox.textContent = "Unknown error.";
    }
  } catch (error) {
    outputBox.textContent = "Failed to connect to Judge0 API.";
  }
}
