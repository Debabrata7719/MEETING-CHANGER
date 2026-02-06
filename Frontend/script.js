const API_BASE = "http://127.0.0.1:8000";

const dropZone = document.getElementById("dropZone");
const fileInput = document.getElementById("fileInput");
const uploadBtn = document.getElementById("uploadBtn");
const uploadStatus = document.getElementById("uploadStatus");
const notesBtn = document.getElementById("notesBtn");
const notesOutput = document.getElementById("notesOutput");
const chatMessages = document.getElementById("chatMessages");
const chatForm = document.getElementById("chatForm");
const chatInput = document.getElementById("chatInput");
const sendBtn = document.getElementById("sendBtn");
const apiStatus = document.getElementById("apiStatus");

const loaderOverlay = document.getElementById("loaderOverlay");
const loaderText = document.getElementById("loaderText");

const recStatus = document.getElementById("recStatus");

let selectedFile = null;
let meetingReady = false;

/* 🔥 active meeting id */
let currentMeetingId = null;


/* =========================
   LOADER
   ========================= */

function showLoader(text = "Processing...") {
  loaderText.textContent = text;
  loaderOverlay.classList.remove("hidden");
}

function hideLoader() {
  loaderOverlay.classList.add("hidden");
}


/* =========================
   UI HELPERS
   ========================= */

function setButtonLoading(button, loading) {
  if (loading) {
    button.classList.add("is-loading");
    button.disabled = true;
  } else {
    button.classList.remove("is-loading");
    button.disabled = false;
  }
}

function setStatus(text, type = "muted") {
  uploadStatus.textContent = text;
  uploadStatus.className = `status ${type}`;
}

function setMeetingReady(value) {
  meetingReady = value;

  notesBtn.disabled = !value;
  chatInput.disabled = !value;
  sendBtn.disabled = !value;

  apiStatus.querySelector("span:last-child").textContent =
    value ? "API: Ready" : "API: Waiting";
}

function addMessage(text, role, options = {}) {
  const message = document.createElement("div");
  message.className = `message ${role}`;

  if (options.loading) message.classList.add("loading");

  message.textContent = text;
  chatMessages.appendChild(message);
  chatMessages.scrollTop = chatMessages.scrollHeight;

  return message;
}

function clearChatPlaceholder() {
  const first = chatMessages.querySelector(".message.assistant");
  if (first && first.textContent.includes("Upload")) {
    first.remove();
  }
}


/* =====================================================
   RECORDING
   ===================================================== */

async function startRecording() {
  try {
    recStatus.textContent = "Status: Recording...";
    setMeetingReady(false);

    showLoader("Recording started...");

    await fetch(`${API_BASE}/start-recording`, {
      method: "POST"
    });

    hideLoader();

  } catch {
    recStatus.textContent = "Recording failed ❌";
    hideLoader();
  }
}

async function stopRecording() {
  try {
    recStatus.textContent = "Status: Processing...";
    showLoader("Processing meeting...");

    const response = await fetch(`${API_BASE}/stop-recording`, {
      method: "POST"
    });

    if (!response.ok) throw new Error();

    const data = await response.json();
    currentMeetingId = data.meeting_id;

    // 🔥 SUCCESS UNDER LIVE RECORDING
    recStatus.innerHTML = `
      Status: Ready ✅ <br>
      <span style="color:#16a34a;font-weight:600;">
       Meeting recorded successfully!✅
      </span>
    `;

    setMeetingReady(true);

    notesOutput.textContent = "Ready to generate highlights.";

    clearChatPlaceholder();

    addMessage(
      "✅ Meeting recorded successfully. You can now ask questions!",
      "assistant"
    );

  } catch {
    recStatus.textContent = "Processing failed ❌";
  } finally {
    hideLoader();
  }
}



/* =========================
   FILE SELECTION
   ========================= */

function handleFileSelection(file) {
  if (!file) return;

  selectedFile = file;

  const sizeMB = (file.size / 1024 / 1024).toFixed(1);

  setStatus(`🎬 ${file.name} (${sizeMB} MB) selected`, "success");
}


/* =========================
   DRAG & DROP
   ========================= */

["dragenter", "dragover"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropZone.classList.add("is-dragover");
  });
});

["dragleave", "drop"].forEach((eventName) => {
  dropZone.addEventListener(eventName, (e) => {
    e.preventDefault();
    dropZone.classList.remove("is-dragover");
  });
});

dropZone.addEventListener("drop", (e) => {
  const file = e.dataTransfer.files[0];
  fileInput.files = e.dataTransfer.files;
  handleFileSelection(file);
});

fileInput.addEventListener("change", (e) => {
  handleFileSelection(e.target.files[0]);
});


/* =========================
   UPLOAD
   ========================= */

uploadBtn.addEventListener("click", async () => {
  if (!selectedFile) {
    setStatus("Please select a file first.");
    return;
  }

  setButtonLoading(uploadBtn, true);
  setMeetingReady(false);
  showLoader("Processing meeting...");

  const formData = new FormData();
  formData.append("file", selectedFile);

  try {
    const response = await fetch(`${API_BASE}/upload`, {
      method: "POST",
      body: formData,
    });

    if (!response.ok) throw new Error("Upload failed");

    const data = await response.json();
    currentMeetingId = data.meeting_id;

    setStatus(`✅ Uploaded & processed: ${selectedFile.name}`, "success");

    setMeetingReady(true);
    notesOutput.textContent = "Ready to generate highlights.";

    clearChatPlaceholder();

    addMessage(
      "✅ Meeting uploaded and processed successfully. Ask anything about it!",
      "assistant"
    );

  } catch {
    setStatus("❌ Upload failed.", "muted");
  } finally {
    hideLoader();
    setButtonLoading(uploadBtn, false);
  }
});


/* =========================
   NOTES
   ========================= */

notesBtn.addEventListener("click", async () => {
  setButtonLoading(notesBtn, true);
  showLoader("Generating highlights...");

  try {
    const response = await fetch(`${API_BASE}/notes`, {
      method: "POST",
    });

    if (!response.ok) throw new Error();

    const data = await response.json();

    notesOutput.textContent = data.notes || "No notes returned.";

  } catch {
    notesOutput.textContent = "Failed to generate notes.";
  } finally {
    hideLoader();
    setButtonLoading(notesBtn, false);
  }
});


/* =========================
   CHAT
   ========================= */

chatForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const question = chatInput.value.trim();
  if (!question || !currentMeetingId) return;

  clearChatPlaceholder();
  addMessage(question, "user");

  chatInput.value = "";

  setButtonLoading(sendBtn, true);
  showLoader("Thinking...");

  const pending = addMessage("Thinking...", "assistant", { loading: true });

  try {
    const response = await fetch(`${API_BASE}/chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        question,
        meeting_id: currentMeetingId
      }),
    });

    if (!response.ok) throw new Error();

    const data = await response.json();

    pending.classList.remove("loading");
    pending.textContent = data.answer || "No response.";

  } catch {
    pending.textContent = "Chat failed.";
  } finally {
    hideLoader();
    setButtonLoading(sendBtn, false);
  }
});


setMeetingReady(false);
