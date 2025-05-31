function startRecognition() {
  fetch('/start_recognition')
    .then(res => res.json())
    .then(data => alert('Recognition ' + data.status));
}

function stopRecognition() {
  fetch('/stop_recognition')
    .then(res => res.json())
    .then(data => alert('Recognition ' + data.status));
}

function refreshLogs() {
  fetch('/unauthorized_logs')
    .then(res => res.json())
    .then(files => {
      const container = document.getElementById('logs');
      container.innerHTML = '';
      files.forEach(file => {
        const img = document.createElement('img');
        img.src = '/snapshots/' + file;
        img.style.maxWidth = '150px';
        img.style.margin = '5px';
        container.appendChild(img);
      });
    });
}
