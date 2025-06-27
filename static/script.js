const socket = io();

const editor = CodeMirror.fromTextArea(document.getElementById("editor"), {
    lineNumbers: true,
    mode: "python",
    theme: "material-darker"
});

let username = prompt("Enter your name:") || "Anonymous";
socket.emit("join", { name: username });

editor.on("change", () => {
    const code = editor.getValue();
    socket.emit("code_change", { code });
});

socket.on("code_update", (data) => {
    if (data.code !== editor.getValue()) {
        const cursor = editor.getCursor();
        editor.setValue(data.code);
        editor.setCursor(cursor);
    }
});

socket.on("chat_message", (data) => {
    const chat = document.getElementById("chat");
    const msg = document.createElement("div");
    msg.innerHTML = `<strong>${data.name}:</strong> ${data.message}`;
    chat.appendChild(msg);
    chat.scrollTop = chat.scrollHeight;
});

document.getElementById("sendBtn").addEventListener("click", () => {
    const input = document.getElementById("chatInput");
    const msg = input.value.trim();
    if (msg) {
        socket.emit("send_message", { message: msg });
        input.value = "";
    }
});

document.getElementById("runBtn").addEventListener("click", async () => {
    const code = editor.getValue();
    const language = document.getElementById("language").value;

    const res = await fetch("/run", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ code: code, language: language })
    });

    const data = await res.json();
    document.getElementById("output").textContent = data.output;
});
