"""
Flask web UI for the TCL TV remote control.
Run: python app.py  then open http://127.0.0.1:5000
"""

import os
import time
from flask import Flask, render_template_string, jsonify, request
from remote import TVRemote, KEYCODES, APPS

app = Flask(__name__)

# Auto-detect connected device, fall back to default
def get_remote():
    device = os.environ.get("TV_DEVICE", "192.168.0.90:5555")
    return TVRemote(device=device)

tv = get_remote()

HTML = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>TV Remote</title>
<style>
:root {
  --bg: #1a1a2e;
  --card: #16213e;
  --btn: #0f3460;
  --btn-hover: #1a4a7a;
  --accent: #e94560;
  --text: #eee;
  --text-dim: #8899aa;
}
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
  background: var(--bg);
  color: var(--text);
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  min-height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
}
.remote {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  max-width: 380px;
  width: 100%;
}
.section {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 4px;
}
.section-title {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 11px;
  letter-spacing: 1px;
  text-transform: uppercase;
  color: var(--text-dim);
  margin-top: 12px;
  margin-bottom: 4px;
}
.btn {
  background: var(--btn);
  color: var(--text);
  border: none;
  border-radius: 12px;
  padding: 16px 8px;
  font-size: 13px;
  font-weight: 600;
  cursor: pointer;
  transition: background 0.15s, transform 0.05s;
  user-select: none;
  text-align: center;
  -webkit-tap-highlight-color: transparent;
}
.btn:hover { background: var(--btn-hover); }
.btn:active { transform: scale(0.95); }
.btn.power { background: var(--accent); }
.btn.power:hover { background: #ff5a75; }
.btn.dpad-center { background: var(--btn); border: 2px solid var(--accent); font-size: 12px; }
.btn.wide { grid-column: span 1; }
.btn-full { grid-column: 1 / -1; }

.dpad {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  grid-template-rows: 1fr 1fr 1fr;
  gap: 6px;
  max-width: 200px;
  margin: 0 auto;
  width: 100%;
}
.dpad .up { grid-column: 2; grid-row: 1; }
.dpad .left { grid-column: 1; grid-row: 2; }
.dpad .center { grid-column: 2; grid-row: 2; }
.dpad .right { grid-column: 3; grid-row: 2; }
.dpad .down { grid-column: 2; grid-row: 3; }

.apps {
  grid-column: 1 / -1;
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 6px;
}
.app-btn {
  font-size: 11px;
  padding: 10px 4px;
}

.status {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 12px;
  color: var(--text-dim);
  padding: 8px;
  min-height: 20px;
}
.status.ok { color: #4ade80; }
.status.err { color: var(--accent); }

.flash {
  position: fixed;
  top: 16px;
  left: 50%;
  transform: translateX(-50%);
  background: var(--card);
  color: var(--text);
  padding: 8px 20px;
  border-radius: 8px;
  font-size: 13px;
  opacity: 0;
  transition: opacity 0.2s;
  pointer-events: none;
  z-index: 100;
}
.flash.show { opacity: 1; }

.tabs {
  grid-column: 1 / -1;
  display: flex;
  gap: 4px;
  margin-bottom: 8px;
}
.tab-btn {
  flex: 1;
  background: var(--card);
  color: var(--text-dim);
  border: none;
  border-radius: 8px 8px 0 0;
  padding: 10px 4px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
}
.tab-btn.active { background: var(--btn); color: var(--text); }
.tab-page { display: none; grid-column: 1 / -1; }
.tab-page.active { display: block; }

.launcher-list { display: grid; gap: 8px; }
.launcher-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card);
  border-radius: 10px;
  padding: 12px 16px;
  border: 2px solid transparent;
}
.launcher-card.default { border-color: var(--accent); }
.launcher-card.disabled { opacity: 0.5; }
.launcher-info { display: flex; flex-direction: column; gap: 2px; }
.launcher-name { font-size: 14px; font-weight: 600; }
.launcher-pkg { font-size: 11px; color: var(--text-dim); }
.launcher-badge {
  font-size: 10px;
  padding: 2px 8px;
  border-radius: 6px;
  font-weight: 600;
}
.badge-default { background: var(--accent); color: #fff; }
.badge-installed { background: #27ae60; color: #fff; }
.badge-off { background: #555; color: #aaa; }
.btn-set {
  background: var(--btn);
  color: var(--text);
  border: none;
  border-radius: 8px;
  padding: 8px 16px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.btn-set:hover { background: var(--btn-hover); }
.btn-set:disabled { opacity: 0.4; cursor: default; }

/* ── Touchpad ── */
.touchpad-area {
  grid-column: 1 / -1;
  height: 220px;
  background: var(--card);
  border: 2px solid var(--btn);
  border-radius: 16px;
  margin-bottom: 8px;
  touch-action: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-dim);
  font-size: 12px;
}
.touchpad-area:active { border-color: var(--accent); }

/* ── Keyboard input ── */
.kb-input {
  grid-column: 1 / -1;
  background: var(--card);
  border: 2px solid var(--btn);
  border-radius: 10px;
  color: var(--text);
  padding: 12px;
  font-size: 16px;
  width: 100%;
  margin-bottom: 4px;
}
.kb-input:focus { border-color: var(--accent); outline: none; }

/* ── Sleep Timer ── */
.timer-display {
  grid-column: 1 / -1;
  text-align: center;
  font-size: 28px;
  font-weight: 700;
  color: var(--accent);
  padding: 20px 0;
  min-height: 72px;
}

/* ── Macros ── */
.macro-list { display: grid; gap: 8px; }
.macro-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  background: var(--card);
  border-radius: 10px;
  padding: 12px 16px;
}
.macro-card-name { font-size: 14px; font-weight: 600; }
.macro-card-cmds { font-size: 11px; color: var(--text-dim); margin-top: 2px; }
.macro-text {
  grid-column: 1 / -1;
  background: var(--card);
  border: 2px solid var(--btn);
  border-radius: 10px;
  color: var(--text);
  padding: 12px;
  font-size: 13px;
  width: 100%;
  min-height: 80px;
  font-family: monospace;
  resize: vertical;
  margin-top: 4px;
}
.macro-text:focus { border-color: var(--accent); outline: none; }
.macro-run {
  background: var(--btn);
  color: var(--text);
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 12px;
  font-weight: 600;
  cursor: pointer;
}
.macro-run:hover { background: var(--btn-hover); }
.macro-del {
  background: transparent;
  color: var(--accent);
  border: 1px solid var(--accent);
  border-radius: 8px;
  padding: 6px 10px;
  font-size: 11px;
  cursor: pointer;
}
</style>
</head>
<body>

<div class="flash" id="flash"></div>

<div class="remote">

  <div class="tabs">
    <button class="tab-btn active" onclick="switchTab('remote')">Remote</button>
    <button class="tab-btn" onclick="switchTab('touchpad')">Touchpad</button>
    <button class="tab-btn" onclick="switchTab('keyboard')">Keyboard</button>
    <button class="tab-btn" onclick="switchTab('timer')">Timer</button>
    <button class="tab-btn" onclick="switchTab('macros')">Macros</button>
    <button class="tab-btn" onclick="switchTab('launchers')">Launchers</button>
  </div>

  <div class="tab-page active" id="tab-remote">

  <div class="section">
    <button class="btn power" onclick="send('power')">⏻ Power</button>
    <button class="btn" onclick="send('home')">⌂ Home</button>
    <button class="btn" onclick="send('back')">← Back</button>
  </div>

  <div class="section">
    <button class="btn" onclick="send('volume_up')">Vol +</button>
    <button class="btn" onclick="send('volume_mute')">🔇 Mute</button>
    <button class="btn" onclick="send('volume_down')">Vol −</button>
  </div>

  <div class="section">
    <button class="btn" onclick="send('channel_up')">CH +</button>
    <button class="btn" onclick="send('info')">ℹ Info</button>
    <button class="btn" onclick="send('channel_down')">CH −</button>
  </div>

  <div class="section-title">DPAD</div>
  <div class="dpad">
    <button class="btn up" onclick="send('dpad_up')">▲</button>
    <button class="btn left" onclick="send('dpad_left')">◄</button>
    <button class="btn dpad-center center" onclick="send('dpad_center')">OK</button>
    <button class="btn right" onclick="send('dpad_right')">►</button>
    <button class="btn down" onclick="send('dpad_down')">▼</button>
  </div>

  <div class="section-title">Playback</div>
  <div class="section">
    <button class="btn" onclick="send('rewind')">⏪</button>
    <button class="btn" onclick="send('play_pause')">⏯</button>
    <button class="btn" onclick="send('fast_forward')">⏩</button>
    <button class="btn" onclick="send('previous')">⏮</button>
    <button class="btn" onclick="send('stop')">⏹</button>
    <button class="btn" onclick="send('next')">⏭</button>
  </div>

  <div class="section-title">Colours</div>
  <div class="section">
    <button class="btn" style="background:#c0392b" onclick="send('red')">Red</button>
    <button class="btn" style="background:#27ae60" onclick="send('green')">Green</button>
    <button class="btn" style="background:#f39c12" onclick="send('yellow')">Yellow</button>
    <button class="btn" style="background:#2980b9" onclick="send('blue')">Blue</button>
    <button class="btn" onclick="send('menu')">☰ Menu</button>
    <button class="btn" onclick="send('guide')">📋 Guide</button>
  </div>

  <div class="section-title">Numbers</div>
  <div class="section">
    <button class="btn" onclick="send('1')">1</button>
    <button class="btn" onclick="send('2')">2</button>
    <button class="btn" onclick="send('3')">3</button>
    <button class="btn" onclick="send('4')">4</button>
    <button class="btn" onclick="send('5')">5</button>
    <button class="btn" onclick="send('6')">6</button>
    <button class="btn" onclick="send('7')">7</button>
    <button class="btn" onclick="send('8')">8</button>
    <button class="btn" onclick="send('9')">9</button>
    <button class="btn" onclick="send('caption')">CC</button>
    <button class="btn" onclick="send('0')">0</button>
    <button class="btn" onclick="send('settings')">⚙ Settings</button>
  </div>

  <div class="section-title">Apps</div>
  <div class="apps" id="apps-grid">
    <!-- filled by JS -->
  </div>

  <div class="section-title">Status</div>
  <div class="status" id="status">Connecting...</div>
  <button class="btn btn-full" onclick="screenshot()">📸 Screenshot</button>
  <button class="btn btn-full" onclick="refreshStatus()">↻ Refresh Status</button>

  </div><!-- /tab-remote -->

  <div class="tab-page" id="tab-launchers">
    <div class="section-title">Installed Launchers</div>
    <div class="launcher-list" id="launcher-list">
      <div style="text-align:center;color:var(--text-dim);padding:20px">Loading...</div>
    </div>
    <button class="btn btn-full" style="margin-top:12px" onclick="loadLaunchers()">↻ Refresh</button>
  </div>

  <!-- ── Touchpad tab ── -->
  <div class="tab-page" id="tab-touchpad">
    <div class="section-title">Touchpad</div>
    <div id="touchpad-area" class="touchpad-area"></div>
    <div class="section" style="margin-top:8px">
      <button class="btn" onclick="send('back')">← Back</button>
      <button class="btn" onclick="send('home')">⌂ Home</button>
      <button class="btn" onclick="send('dpad_center')">OK</button>
    </div>
    <div class="section">
      <button class="btn" onclick="send('dpad_up')">▲</button>
      <button class="btn" onclick="send('dpad_left')">◄</button>
      <button class="btn" onclick="send('dpad_right')">►</button>
      <button class="btn" onclick="send('dpad_down')">▼</button>
    </div>
  </div>

  <!-- ── Keyboard tab ── -->
  <div class="tab-page" id="tab-keyboard">
    <div class="section-title">Keyboard</div>
    <input type="text" id="kb-input" class="kb-input" placeholder="Type text for TV...">
    <button class="btn btn-full" style="margin-top:8px" onclick="sendText()">Send Text</button>
    <div class="section" style="margin-top:8px">
      <button class="btn" onclick="sendKey('enter')">Enter</button>
      <button class="btn" onclick="sendKey('del')">Del</button>
      <button class="btn" onclick="sendKey('space')">Space</button>
    </div>
  </div>

  <!-- ── Sleep Timer tab ── -->
  <div class="tab-page" id="tab-timer">
    <div class="section-title">Sleep Timer</div>
    <div class="timer-display" id="timer-display">No timer</div>
    <div class="section" style="margin-top:8px">
      <button class="btn" onclick="setTimer(15)">15 min</button>
      <button class="btn" onclick="setTimer(30)">30 min</button>
      <button class="btn" onclick="setTimer(45)">45 min</button>
      <button class="btn" onclick="setTimer(60)">60 min</button>
      <button class="btn" onclick="setTimer(90)">90 min</button>
      <button class="btn" style="background:var(--accent)" onclick="cancelTimer()">Cancel</button>
    </div>
  </div>

  <!-- ── Macros tab ── -->
  <div class="tab-page" id="tab-macros">
    <div class="section-title">Macros</div>
    <div class="macro-list" id="macro-list"></div>
    <div class="section-title" style="margin-top:16px">Create Macro</div>
    <input type="text" id="macro-name" class="kb-input" placeholder="Macro name (e.g. Movie Night)">
    <textarea id="macro-cmds" class="macro-text" placeholder="One command per line. Examples:&#10;launch netflix&#10;volume_up&#10;wait 2&#10;dpad_center"></textarea>
    <button class="btn btn-full" style="margin-top:8px" onclick="saveMacro()">Save Macro</button>
  </div>

</div>

<script>
const flash = document.getElementById('flash');
const statusEl = document.getElementById('status');

function showFlash(msg, ok=true) {
  flash.textContent = msg;
  flash.style.color = ok ? '#4ade80' : '#e94560';
  flash.classList.add('show');
  setTimeout(() => flash.classList.remove('show'), 1200);
}

async function send(key) {
  try {
    const r = await fetch('/api/key/' + key, { method: 'POST' });
    const data = await r.json();
    if (data.ok) {
      showFlash(key);
    } else {
      showFlash(data.error || 'Error', false);
    }
  } catch(e) {
    showFlash('Connection error', false);
  }
}

async function launchApp(name) {
  try {
    const r = await fetch('/api/launch/' + name, { method: 'POST' });
    const data = await r.json();
    if (data.ok) showFlash('Launched ' + name);
    else showFlash(data.error || 'Error', false);
  } catch(e) {
    showFlash('Connection error', false);
  }
}

async function screenshot() {
  showFlash('Taking screenshot...');
  try {
    const r = await fetch('/api/screenshot', { method: 'POST' });
    const data = await r.json();
    if (data.ok) {
      showFlash('Screenshot saved');
      window.open('/screenshot', '_blank');
    } else {
      showFlash(data.error || 'Error', false);
    }
  } catch(e) {
    showFlash('Connection error', false);
  }
}

async function refreshStatus() {
  try {
    const r = await fetch('/api/status');
    const data = await r.json();
    if (data.ok) {
      statusEl.textContent = data.app;
      statusEl.className = 'status ' + (data.awake ? 'ok' : 'err');
    }
  } catch(e) {
    statusEl.textContent = 'Disconnected';
    statusEl.className = 'status err';
  }
}

// build app buttons
fetch('/api/apps').then(r => r.json()).then(data => {
  if (!data.apps) return;
  const grid = document.getElementById('apps-grid');
  const icons = {
    netflix: '🔴 Netflix', youtube: '▶ YouTube', disney: '🟣 Disney+',
    prime: '🔵 Prime', rakuten: 'Rakuten', bbc: 'BBC',
    itv: 'ITV', channel4: 'CH4', channel5: 'CH5',
    stan: 'Stan', youtube_music: '🎵 YT Music',
    launcher: 'Launcher', browser: 'Browser',
    assistant: 'Assistant', google_play: 'Play Store',
  };
  for (const [name, pkg] of Object.entries(data.apps)) {
    const btn = document.createElement('button');
    btn.className = 'btn app-btn';
    btn.textContent = icons[name] || name;
    btn.onclick = () => launchApp(name);
    grid.appendChild(btn);
  }
});

// tab switching
function switchTab(name) {
  document.querySelectorAll('.tab-btn').forEach(b => b.classList.remove('active'));
  document.querySelectorAll('.tab-page').forEach(p => p.classList.remove('active'));
  event.target.classList.add('active');
  document.getElementById('tab-' + name).classList.add('active');
  if (name === 'launchers') loadLaunchers();
}

// launcher management
async function loadLaunchers() {
  const list = document.getElementById('launcher-list');
  list.innerHTML = '<div style="text-align:center;color:var(--text-dim);padding:20px">Loading...</div>';
  try {
    const r = await fetch('/api/launchers');
    const data = await r.json();
    if (!data.ok || !data.launchers) {
      list.innerHTML = '<div style="text-align:center;color:var(--accent);padding:20px">Error loading launchers</div>';
      return;
    }
    if (data.launchers.length === 0) {
      list.innerHTML = '<div style="text-align:center;color:var(--text-dim);padding:20px">No launchers installed</div>';
      return;
    }
    list.innerHTML = '';
    for (const l of data.launchers) {
      const card = document.createElement('div');
      card.className = 'launcher-card' + (l.default ? ' default' : '') + (l.enabled ? '' : ' disabled');
      let badge = '';
      if (l.default) badge = '<span class="launcher-badge badge-default">Default</span>';
      else if (l.enabled) badge = '<span class="launcher-badge badge-installed">Installed</span>';
      else badge = '<span class="launcher-badge badge-off">Disabled</span>';
      const btnDisabled = l.default ? 'disabled' : '';
      card.innerHTML = `
        <div class="launcher-info">
          <span class="launcher-name">${l.label}</span>
          <span class="launcher-pkg">${l.package}</span>
        </div>
        <div style="display:flex;gap:8px;align-items:center">
          ${badge}
          <button class="btn-set" onclick="setLauncher('${l.package}')" ${btnDisabled}>Set as home</button>
        </div>`;
      list.appendChild(card);
    }
  } catch(e) {
    list.innerHTML = '<div style="text-align:center;color:var(--accent);padding:20px">Connection error</div>';
  }
}

async function setLauncher(pkg) {
  showFlash('Switching launcher...');
  try {
    const r = await fetch('/api/launcher/set', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({package: pkg})
    });
    const data = await r.json();
    if (data.ok) {
      showFlash('Launcher switched');
      loadLaunchers();
    } else {
      showFlash(data.error || 'Error', false);
    }
  } catch(e) {
    showFlash('Connection error', false);
  }
}

// initial status
refreshStatus();

// ── Touchpad ──
(function() {
  const pad = document.getElementById('touchpad-area');
  if (!pad) return;
  let startX = 0, startY = 0, lastTap = 0;

  pad.addEventListener('touchstart', e => {
    e.preventDefault();
    const t = e.touches[0];
    startX = t.clientX; startY = t.clientY;
  }, {passive: false});

  pad.addEventListener('touchend', e => {
    e.preventDefault();
    const t = e.changedTouches[0];
    const dx = t.clientX - startX;
    const dy = t.clientY - startY;
    const dist = Math.sqrt(dx*dx + dy*dy);
    if (dist < 10) {
      // tap = click
      const now = Date.now();
      if (now - lastTap < 300) {
        send('dpad_center'); // double tap = OK
      } else {
        send('dpad_center'); // single tap = OK too
      }
      lastTap = now;
    } else {
      // swipe -> dpad direction
      if (Math.abs(dx) > Math.abs(dy)) {
        send(dx > 0 ? 'dpad_right' : 'dpad_left');
      } else {
        send(dy > 0 ? 'dpad_down' : 'dpad_up');
      }
    }
  }, {passive: false});

  // mouse fallback for desktop testing
  pad.addEventListener('click', () => send('dpad_center'));
})();

// ── Keyboard ──
async function sendText() {
  const txt = document.getElementById('kb-input').value;
  if (!txt) return;
  try {
    const r = await fetch('/api/text', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({text: txt})
    });
    const data = await r.json();
    if (data.ok) {
      showFlash('Sent: ' + txt);
      document.getElementById('kb-input').value = '';
    } else {
      showFlash(data.error || 'Error', false);
    }
  } catch(e) { showFlash('Connection error', false); }
}

async function sendKey(k) {
  try {
    const r = await fetch('/api/key/' + k, { method: 'POST' });
    const data = await r.json();
    if (!data.ok) showFlash(data.error || 'Error', false);
  } catch(e) { showFlash('Connection error', false); }
}

// ── Sleep Timer ──
let timerInterval = null;
let timerEnd = null;

function setTimer(minutes) {
  cancelTimer();
  timerEnd = Date.now() + minutes * 60000;
  showFlash('Timer set: ' + minutes + ' min');
  updateTimer();
  timerInterval = setInterval(updateTimer, 1000);
}

function cancelTimer() {
  if (timerInterval) { clearInterval(timerInterval); timerInterval = null; }
  timerEnd = null;
  document.getElementById('timer-display').textContent = 'No timer';
}

function updateTimer() {
  if (!timerEnd) return;
  const remaining = timerEnd - Date.now();
  if (remaining <= 0) {
    clearInterval(timerInterval);
    timerInterval = null;
    document.getElementById('timer-display').textContent = 'Powering off...';
    fetch('/api/key/power', { method: 'POST' });
    setTimeout(() => { document.getElementById('timer-display').textContent = 'TV powered off'; }, 2000);
    return;
  }
  const m = Math.floor(remaining / 60000);
  const s = Math.floor((remaining % 60000) / 1000);
  document.getElementById('timer-display').textContent =
    String(m).padStart(2,'0') + ':' + String(s).padStart(2,'0');
}

// ── Macros ──
const MACRO_KEY = 'tv_macros';

function loadMacros() {
  const list = document.getElementById('macro-list');
  let macros = JSON.parse(localStorage.getItem(MACRO_KEY) || '[]');
  if (macros.length === 0) {
    list.innerHTML = '<div style="text-align:center;color:var(--text-dim);padding:16px">No macros yet</div>';
    return;
  }
  list.innerHTML = '';
  macros.forEach((m, i) => {
    const card = document.createElement('div');
    card.className = 'macro-card';
    card.innerHTML = `
      <div>
        <div class="macro-card-name">${m.name}</div>
        <div class="macro-card-cmds">${m.cmds.replace(/\\n/g, ' → ')}</div>
      </div>
      <div style="display:flex;gap:8px">
        <button class="macro-run" onclick="runMacro(${i})">Run</button>
        <button class="macro-del" onclick="deleteMacro(${i})">✕</button>
      </div>`;
    list.appendChild(card);
  });
}

function saveMacro() {
  const name = document.getElementById('macro-name').value.trim();
  const cmds = document.getElementById('macro-cmds').value.trim();
  if (!name || !cmds) { showFlash('Need name and commands', false); return; }
  let macros = JSON.parse(localStorage.getItem(MACRO_KEY) || '[]');
  macros.push({ name, cmds });
  localStorage.setItem(MACRO_KEY, JSON.stringify(macros));
  document.getElementById('macro-name').value = '';
  document.getElementById('macro-cmds').value = '';
  showFlash('Macro saved');
  loadMacros();
}

function deleteMacro(i) {
  let macros = JSON.parse(localStorage.getItem(MACRO_KEY) || '[]');
  macros.splice(i, 1);
  localStorage.setItem(MACRO_KEY, JSON.stringify(macros));
  loadMacros();
}

async function runMacro(i) {
  let macros = JSON.parse(localStorage.getItem(MACRO_KEY) || '[]');
  const m = macros[i];
  if (!m) return;
  showFlash('Running: ' + m.name);
  try {
    const r = await fetch('/api/macro/run', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({cmds: m.cmds})
    });
    const data = await r.json();
    if (data.ok) showFlash('Done: ' + m.name);
    else showFlash(data.error || 'Error', false);
  } catch(e) { showFlash('Connection error', false); }
}

// switchTab extension: load macros when tab opens
const origSwitchTab = switchTab;
switchTab = function(name) {
  origSwitchTab(name);
  if (name === 'macros') loadMacros();
};
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(HTML)


@app.route("/api/key/<key>", methods=["POST"])
def api_key(key):
    if key not in KEYCODES:
        return jsonify({"ok": False, "error": f"Unknown key: {key}"})
    try:
        tv._keyevent(KEYCODES[key])
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/launch/<name>", methods=["POST"])
def api_launch(name):
    try:
        tv.launch_app(name)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/apps")
def api_apps():
    return jsonify({"apps": APPS})


@app.route("/api/status")
def api_status():
    try:
        app_str = tv.current_app()
        awake = tv.is_awake()
        return jsonify({"ok": True, "app": app_str, "awake": awake})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e), "awake": False})


@app.route("/api/screenshot", methods=["POST"])
def api_screenshot():
    try:
        path = os.path.join(os.path.dirname(__file__), "screenshot.png")
        tv.screenshot(path)
        return jsonify({"ok": True, "path": path})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/screenshot")
def serve_screenshot():
    from flask import send_file
    path = os.path.join(os.path.dirname(__file__), "screenshot.png")
    if os.path.exists(path):
        return send_file(path, mimetype="image/png")
    return "No screenshot yet", 404


@app.route("/api/launchers")
def api_launchers():
    try:
        launchers = tv.list_launchers()
        return jsonify({"ok": True, "launchers": launchers})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/launcher/set", methods=["POST"])
def api_set_launcher():
    try:
        data = request.get_json()
        pkg = data.get("package")
        if not pkg:
            return jsonify({"ok": False, "error": "No package specified"})
        tv.set_launcher(pkg)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/text", methods=["POST"])
def api_text():
    try:
        data = request.get_json()
        text = data.get("text", "")
        if not text:
            return jsonify({"ok": False, "error": "No text provided"})
        tv.type_text(text)
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


@app.route("/api/macro/run", methods=["POST"])
def api_macro_run():
    try:
        data = request.get_json()
        cmds_raw = data.get("cmds", "")
        if not cmds_raw.strip():
            return jsonify({"ok": False, "error": "No commands"})
        lines = [l.strip() for l in cmds_raw.strip().splitlines() if l.strip()]
        for line in lines:
            parts = line.split(None, 1)
            cmd = parts[0].lower()
            arg = parts[1] if len(parts) > 1 else ""
            if cmd == "wait" and arg:
                time.sleep(float(arg))
            elif cmd == "launch" and arg:
                tv.launch_app(arg)
            elif cmd == "type" and arg:
                tv.type_text(arg)
            elif cmd in KEYCODES:
                tv._keyevent(KEYCODES[cmd])
            elif hasattr(tv, cmd) and cmd not in ("shell", "_shell", "_keyevent"):
                getattr(tv, cmd)()
            else:
                return jsonify({"ok": False, "error": f"Unknown command: {cmd}"})
        return jsonify({"ok": True})
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)})


if __name__ == "__main__":
    print(f"TV Remote web UI running at http://192.168.0.217:5000")
    print(f"Device: {tv.device}")
    app.run(host="0.0.0.0", port=5000, debug=False)
