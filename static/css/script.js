const logEl = document.getElementById('log');
const snapshotGrid = document.getElementById('snapshotGrid');
const toastEl = document.getElementById('toast');

function showToast(message) {
  toastEl.textContent = message;
  toastEl.classList.remove('hidden');
  setTimeout(() => toastEl.classList.add('hidden'), 3000);
}

function log(message) {
  const time = new Date().toLocaleTimeString();
  const newLine = document.createElement('div');
  newLine.textContent = `[${time}] ${message}`;
  newLine.classList.add('log-entry');
  newLine.style.opacity = 0;
  logEl.appendChild(newLine);
  setTimeout(() => (newLine.style.opacity = 1), 100);
  logEl.scrollTop = logEl.scrollHeight;
}

async function startRecognition() {
  showToast("Starting recognition...");
  const res = await fetch('/start_recognition', { method: 'POST' });
  const data = await res.json();
  log(`Recognition: ${data.status}`);
}

async function stopRecognition() {
  showToast("Stopping recognition...");
  const res = await fetch('/stop_recognition', { method: 'POST' });
  const data = await res.json();
  log(`Recognition: ${data.status}`);
}

async function viewLogs() {
  showToast("Loading logs...");
  const res = await fetch('/unauthorized_logs');
  const data = await res.json();
  snapshotGrid.innerHTML = '';
  if (data.snapshots.length === 0) {
    log("No unauthorized snapshots found.");
    return;
  }
  data.snapshots.forEach(snap => {
    const div = document.createElement('div');
    div.className = 'snapshot';
    const img = document.createElement('img');
    img.src = `/unauthorized_snapshots/${snap}`;
    img.alt = snap;
    const p = document.createElement('p');
    p.textContent = snap;
    div.appendChild(img);
    div.appendChild(p);
    snapshotGrid.appendChild(div);
  });
  log(`Loaded ${data.snapshots.length} unauthorized snapshots.`);
}

function stopViewingLogs() {
  snapshotGrid.innerHTML = '';
  log("Stopped viewing unauthorized snapshots.");
}

function openLogsInNewTab() {
  window.open('/unauthorized_logs', '_blank');
}

function toggleDarkMode() {
  document.body.classList.toggle('dark-mode');
  log("Toggled dark mode.");
}

document.getElementById('startBtn').addEventListener('click', startRecognition);
document.getElementById('stopBtn').addEventListener('click', stopRecognition);
document.getElementById('viewLogsBtn').addEventListener('click', viewLogs);
document.getElementById('stop-unauth-logs-btn').addEventListener('click', stopViewingLogs);
document.getElementById('openLogsNewTabBtn').addEventListener('click', openLogsInNewTab);
document.getElementById('toggleDarkMode').addEventListener('click', toggleDarkMode);
