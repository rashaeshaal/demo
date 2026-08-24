const backendUrlInput = document.querySelector("#backendUrl");
const saveBackendUrlButton = document.querySelector("#saveBackendUrl");
const refreshNowButton = document.querySelector("#refreshNow");
const connectionStatus = document.querySelector("#connectionStatus");
const totalMessages = document.querySelector("#totalMessages");
const connectedPcs = document.querySelector("#connectedPcs");
const lastUpdate = document.querySelector("#lastUpdate");
const messagesBody = document.querySelector("#messagesBody");
const pcSummary = document.querySelector("#pcSummary");
const ONLINE_TIMEOUT_MS = 10000;

const savedBackendUrl = localStorage.getItem("backendUrl");
if (savedBackendUrl) {
  backendUrlInput.value = savedBackendUrl;
}

function getBackendUrl() {
  return backendUrlInput.value.replace(/\/$/, "");
}

function setStatus(type, text) {
  connectionStatus.className = `status ${type}`;
  connectionStatus.querySelector("span:last-child").textContent = text;
}

function formatTime(value) {
  if (!value) return "-";
  return new Date(value).toLocaleTimeString();
}

function isOnline(message) {
  return Date.now() - new Date(message.receivedAt).getTime() <= ONLINE_TIMEOUT_MS;
}

function renderMessages(messages) {
  const latest = messages.slice(-20).reverse();

  if (latest.length === 0) {
    messagesBody.innerHTML = '<tr><td colspan="6" class="empty">Waiting for data...</td></tr>';
    return;
  }

  messagesBody.innerHTML = latest
    .map((message) => {
      const payload = message.payload || {};
      const status = payload.status || "-";
      const badgeClass = status === "warning" ? "badge warning" : "badge";

      return `
        <tr>
          <td>${message.id}</td>
          <td>${message.pcId}</td>
          <td><span class="${badgeClass}">${status}</span></td>
          <td>${payload.temperature ?? "-"} C</td>
          <td>${payload.pressure ?? "-"}</td>
          <td>${formatTime(message.receivedAt)}</td>
        </tr>
      `;
    })
    .join("");
}

function renderPcSummary(messages) {
  const byPc = new Map();

  for (const message of messages) {
    byPc.set(message.pcId, message);
  }

  const pcMessages = Array.from(byPc.values());
  const onlineCount = pcMessages.filter(isOnline).length;
  connectedPcs.textContent = onlineCount;

  if (byPc.size === 0) {
    pcSummary.innerHTML = '<div class="empty-block">No PC data yet.</div>';
    return;
  }

  pcSummary.innerHTML = pcMessages
    .sort((a, b) => {
      const aOnline = isOnline(a);
      const bOnline = isOnline(b);

      if (aOnline !== bOnline) {
        return aOnline ? -1 : 1;
      }

      return a.pcId.localeCompare(b.pcId);
    })
    .map((message) => {
      const payload = message.payload || {};
      const online = isOnline(message);
      const itemClass = online ? "pc-item" : "pc-item offline";
      const stateLabel = online ? payload.status || "online" : "offline";

      return `
        <div class="${itemClass}">
          <div class="pc-name">
            <span>${message.pcId}</span>
            <span>${stateLabel}</span>
          </div>
          <div class="pc-meta">
            Last message #${message.sequence} at ${formatTime(message.receivedAt)}
          </div>
        </div>
      `;
    })
    .join("");
}

async function loadMessages() {
  try {
    const response = await fetch(`${getBackendUrl()}/messages`);

    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }

    const data = await response.json();
    const messages = data.messages || [];

    totalMessages.textContent = data.count || messages.length;
    lastUpdate.textContent = new Date().toLocaleTimeString();
    renderMessages(messages);
    renderPcSummary(messages);
    setStatus("ok", "Connected");
  } catch (error) {
    setStatus("error", "Offline");
    console.error(error);
  }
}

saveBackendUrlButton.addEventListener("click", () => {
  localStorage.setItem("backendUrl", getBackendUrl());
  loadMessages();
});

refreshNowButton.addEventListener("click", loadMessages);

loadMessages();
setInterval(loadMessages, 2000);
