/**
 * app.js — VSeq Main Application
 *
 * Orchestrates: DemoGenerator, SerialManager, WaveformRenderer, and all UI.
 */

import { DemoGenerator, DEFAULT_CHANNELS, CHANNEL_COLORS } from './demo.js';
import { SerialManager }  from './serial.js';
import { WaveformRenderer } from './renderer.js';

/* ═══════════════════════════════════════════════════════
   DATA STORE
═══════════════════════════════════════════════════════ */
const MAX_SAMPLES = 200_000; // ~200 s at 1 kSa/s per channel

const store = {
  timestamps: [],
  voltages:   Array.from({ length: 10 }, () => []),
};

/* ═══════════════════════════════════════════════════════
   APP STATE
═══════════════════════════════════════════════════════ */
const state = {
  channels: DEFAULT_CHANNELS.map((d, i) => ({
    index:       i,
    name:        d.name,
    color:       CHANNEL_COLORS[i],
    visible:     true,
    vMin:        d.vMin,
    vMax:        d.vMax,
    threshold:   d.threshold,
    highlighted: false,
  })),

  demoMode:  true,
  capturing: false,
  connected: false,

  sampleCount:    0,
  lastBatchTime:  0,
  sampleRate:     0,
};

/* ═══════════════════════════════════════════════════════
   MODULES
═══════════════════════════════════════════════════════ */
const demo   = new DemoGenerator();
const serial = new SerialManager();
let   renderer = null;

/* ═══════════════════════════════════════════════════════
   DATA INGESTION  — called by demo or serial
═══════════════════════════════════════════════════════ */
function ingestData(timestamps, voltages) {
  const n = timestamps.length;
  if (n === 0) return;

  for (let i = 0; i < n; i++) {
    store.timestamps.push(timestamps[i]);
    for (let ch = 0; ch < 10; ch++) {
      store.voltages[ch].push(voltages[ch][i] ?? 0);
    }
  }

  // Trim oldest samples if over limit
  if (store.timestamps.length > MAX_SAMPLES) {
    const excess = store.timestamps.length - MAX_SAMPLES;
    store.timestamps.splice(0, excess);
    for (let ch = 0; ch < 10; ch++) store.voltages[ch].splice(0, excess);
  }

  // Rolling sample-rate estimate
  state.sampleCount += n;
  const now = performance.now();
  if (now - state.lastBatchTime >= 500) {
    const elapsed      = (now - state.lastBatchTime) / 1000;
    state.sampleRate   = Math.round(state.sampleCount / elapsed);
    state.sampleCount  = 0;
    state.lastBatchTime = now;
  }

  updateSidebarValues();
  updateStatusBar();
}

/* ═══════════════════════════════════════════════════════
   RENDER LOOP
═══════════════════════════════════════════════════════ */
function renderLoop() {
  if (renderer) {
    renderer.render({
      channels:   state.channels,
      timestamps: store.timestamps,
      voltages:   store.voltages,
    });
    checkTrigger();
    updateBottomBar();
  }
  requestAnimationFrame(renderLoop);
}

/* ═══════════════════════════════════════════════════════
   SIDEBAR — Channel Cards
═══════════════════════════════════════════════════════ */
function buildSidebar() {
  const list = document.getElementById('channel-list');
  list.innerHTML = '';

  state.channels.forEach((ch) => {
    const card = document.createElement('div');
    card.className = 'ch-card';
    card.id        = `ch-card-${ch.index}`;
    card.style.borderLeftColor = ch.color;

    card.innerHTML = `
      <div class="ch-card-top">
        <div class="ch-label">
          <div class="ch-color-dot" id="dot-${ch.index}"
               style="background:${ch.color};box-shadow:0 0 6px ${ch.color}80"
               title="Click to cycle color"></div>
          <span class="ch-name" id="name-${ch.index}"
                title="Double-click to rename">${ch.name}</span>
        </div>
        <button class="ch-vis-btn" id="vis-${ch.index}" title="Toggle visibility">👁</button>
      </div>
      <div class="ch-value" id="val-${ch.index}" style="color:${ch.color}">— V</div>
      <div class="ch-range">
        <span>${ch.vMin}V</span>
        <div class="ch-range-bar">
          <div class="ch-range-fill" id="fill-${ch.index}"
               style="background:${ch.color};width:0%"></div>
        </div>
        <span>${ch.vMax}V</span>
      </div>
      <div class="ch-threshold-row">
        <span class="ch-thr-label">Thr:</span>
        <input class="ch-thr-input" id="thr-${ch.index}"
               type="number" step="0.05" min="${ch.vMin}" max="${ch.vMax}"
               value="${ch.threshold !== null ? ch.threshold.toFixed(2) : ''}"
               placeholder="—">
        <span class="ch-thr-unit">V</span>
      </div>
    `;

    list.appendChild(card);

    /* Visibility toggle */
    document.getElementById(`vis-${ch.index}`).addEventListener('click', (e) => {
      e.stopPropagation();
      ch.visible = !ch.visible;
      card.classList.toggle('hidden-ch', !ch.visible);
    });

    /* Double-click to rename */
    bindRename(ch);

    /* Threshold */
    document.getElementById(`thr-${ch.index}`).addEventListener('input', (e) => {
      const v = parseFloat(e.target.value);
      ch.threshold = isNaN(v) ? null : v;
    });

    /* Highlight strip on hover */
    card.addEventListener('mouseenter', () => { ch.highlighted = true; });
    card.addEventListener('mouseleave', () => { ch.highlighted = false; });

    /* Color cycle on dot click */
    document.getElementById(`dot-${ch.index}`).addEventListener('click', () => {
      const idx = CHANNEL_COLORS.indexOf(ch.color);
      ch.color  = CHANNEL_COLORS[(idx + 1) % CHANNEL_COLORS.length];
      applyChannelColor(ch);
    });
  });
}

function bindRename(ch) {
  const nameEl = document.getElementById(`name-${ch.index}`);
  if (!nameEl) return;
  nameEl.addEventListener('dblclick', () => {
    const input = document.createElement('input');
    input.type      = 'text';
    input.className = 'ch-name-input';
    input.value     = ch.name;
    nameEl.replaceWith(input);
    input.focus();
    input.select();

    const commit = () => {
      ch.name = input.value.trim() || ch.name;
      const span = document.createElement('span');
      span.id        = `name-${ch.index}`;
      span.className = 'ch-name';
      span.title     = 'Double-click to rename';
      span.textContent = ch.name;
      input.replaceWith(span);
      bindRename(ch);
      updateTriggerChannelSelect();
    };
    input.addEventListener('blur',   commit);
    input.addEventListener('keydown', (ke) => {
      if (ke.key === 'Enter')  commit();
      if (ke.key === 'Escape') { input.value = ch.name; commit(); }
    });
  });
}

function applyChannelColor(ch) {
  const dot  = document.getElementById(`dot-${ch.index}`);
  const val  = document.getElementById(`val-${ch.index}`);
  const fill = document.getElementById(`fill-${ch.index}`);
  const card = document.getElementById(`ch-card-${ch.index}`);
  if (dot)  { dot.style.background  = ch.color; dot.style.boxShadow = `0 0 6px ${ch.color}80`; }
  if (val)  val.style.color         = ch.color;
  if (fill) fill.style.background   = ch.color;
  if (card) card.style.borderLeftColor = ch.color;
}

function updateSidebarValues() {
  state.channels.forEach((ch) => {
    const samples = store.voltages[ch.index];
    if (!samples || samples.length === 0) return;
    const v   = samples[samples.length - 1];
    const pct = Math.max(0, Math.min(100, ((v - ch.vMin) / (ch.vMax - ch.vMin)) * 100));
    const valEl  = document.getElementById(`val-${ch.index}`);
    const fillEl = document.getElementById(`fill-${ch.index}`);
    if (valEl)  valEl.textContent   = v.toFixed(3) + ' V';
    if (fillEl) fillEl.style.width  = pct.toFixed(1) + '%';
  });
}

/* ═══════════════════════════════════════════════════════
   TRIGGER CHANNEL SELECT
═══════════════════════════════════════════════════════ */
function updateTriggerChannelSelect() {
  const sel = document.getElementById('trig-ch');
  const cur = sel.value;
  sel.innerHTML = '<option value="-1">— Off —</option>';
  state.channels.forEach((ch) => {
    const opt = document.createElement('option');
    opt.value       = ch.index;
    opt.textContent = `CH${ch.index} ${ch.name}`;
    sel.appendChild(opt);
  });
  sel.value = cur;
}

/* ═══════════════════════════════════════════════════════
   STATUS & BOTTOM BAR
═══════════════════════════════════════════════════════ */
function updateStatusBar() {
  const badge = document.getElementById('status-badge');
  const text  = document.getElementById('status-text');
  const srEl  = document.getElementById('sample-rate-display');
  const elEl  = document.getElementById('elapsed-display');

  badge.className = 'status-badge';
  if (state.capturing && state.connected) {
    badge.classList.add('status-running');
    text.textContent = 'LIVE';
  } else if (state.capturing && state.demoMode) {
    badge.classList.add('status-demo');
    text.textContent = 'DEMO';
  } else if (state.connected) {
    badge.classList.add('status-connected');
    text.textContent = 'USB';
  } else {
    badge.classList.add('status-idle');
    text.textContent = 'IDLE';
  }

  const rate = state.sampleRate;
  srEl.textContent = rate >= 1000
    ? (rate / 1000).toFixed(1) + ' kSa/s'
    : rate + ' Sa/s';

  const lastT = store.timestamps.length
    ? store.timestamps[store.timestamps.length - 1]
    : 0;
  elEl.textContent = (lastT / 1000).toFixed(1) + 's';
}

function updateBottomBar() {
  if (!renderer) return;

  document.getElementById('buf-size').textContent =
    'Buf: ' + (store.timestamps.length / 1000).toFixed(1) + 'k pts';

  const vw = renderer.viewWindow;
  const fmtVw = vw >= 1000
    ? (vw / 1000).toFixed(vw < 10000 ? 2 : 1) + 's'
    : vw.toFixed(0) + 'ms';
  document.getElementById('view-range').textContent = 'View: ' + fmtVw;

  // Sync zoom slider
  const logVal = Math.log10(Math.max(20, vw) / 20) / Math.log10(3000);
  document.getElementById('zoom-slider').value = (logVal * 100).toFixed(1);
  document.getElementById('tb-display').textContent = fmtVw;

  // Follow button
  document.getElementById('btn-follow').classList.toggle('inactive', !renderer.following);

  updateCursorDeltas();
}

function updateCursorDeltas() {
  const c1 = renderer?.cursor1T;
  const c2 = renderer?.cursor2T;
  if (c1 !== null && c1 !== undefined && c2 !== null && c2 !== undefined) {
    const dt = Math.abs(c2 - c1);
    const dT = dt < 1   ? (dt * 1000).toFixed(0) + ' μs'
             : dt < 1000 ? dt.toFixed(2) + ' ms'
             : (dt / 1000).toFixed(3) + ' s';
    document.getElementById('delta-t').textContent  = 'ΔT: ' + dT;
    document.getElementById('freq-est').textContent =
      dt > 0 ? 'f: ' + (1000 / dt).toFixed(1) + ' Hz' : 'f: —';

    let dvSum = 0, dvCount = 0;
    state.channels.forEach((ch) => {
      if (!ch.visible) return;
      const v1 = renderer.valueAtTime(store.voltages[ch.index], store.timestamps, c1);
      const v2 = renderer.valueAtTime(store.voltages[ch.index], store.timestamps, c2);
      if (v1 !== null && v2 !== null) { dvSum += Math.abs(v2 - v1); dvCount++; }
    });
    document.getElementById('delta-v').textContent =
      dvCount ? 'ΔV: ' + (dvSum / dvCount).toFixed(3) + ' V' : 'ΔV: —';
  } else {
    document.getElementById('delta-t').textContent  = 'ΔT: —';
    document.getElementById('delta-v').textContent  = 'ΔV: —';
    document.getElementById('freq-est').textContent = 'f: —';
  }
}

/* ═══════════════════════════════════════════════════════
   CURSOR TOOLTIP
═══════════════════════════════════════════════════════ */
function showCursorTip(t, xPx, yPx) {
  const tip    = document.getElementById('cursor-tip');
  if (t === null || t === undefined || !state.capturing) {
    tip.classList.add('hidden');
    return;
  }

  const tFmt = t < 1000 ? t.toFixed(2) + ' ms' : (t / 1000).toFixed(3) + ' s';
  document.getElementById('ct-time').textContent = 't = ' + tFmt;

  const valEl = document.getElementById('ct-values');
  valEl.innerHTML = '';
  state.channels.forEach((ch) => {
    if (!ch.visible) return;
    const v = renderer.valueAtTime(store.voltages[ch.index], store.timestamps, t);
    if (v === null) return;
    const row = document.createElement('div');
    row.className = 'ct-row';
    row.innerHTML = `
      <span class="ct-ch-name" style="color:${ch.color}">CH${ch.index}</span>
      <span class="ct-v" style="color:${ch.color}">${v.toFixed(3)}V</span>
    `;
    valEl.appendChild(row);
  });

  // Position near cursor, stay inside viewport
  const wrap = document.getElementById('waveform-wrap');
  const rect  = wrap.getBoundingClientRect();
  const tipW  = 150;
  const offX  = xPx - rect.left + 14;
  const offY  = Math.max(4, yPx - rect.top - 20);

  tip.style.left = (offX + tipW + rect.left > window.innerWidth)
    ? (xPx - rect.left - tipW - 12) + 'px'
    : offX + 'px';
  tip.style.top  = offY + 'px';
  tip.classList.remove('hidden');
}

/* ═══════════════════════════════════════════════════════
   TOOLBAR CONTROLS
═══════════════════════════════════════════════════════ */
function setupToolbar() {

  /* ── Demo toggle ── */
  const btnDemo = document.getElementById('btn-demo');
  btnDemo.addEventListener('click', () => {
    state.demoMode = !state.demoMode;
    btnDemo.classList.toggle('active', state.demoMode);
    document.getElementById('hw-info').textContent = state.demoMode ? 'Demo' : 'USB';
    if (!state.demoMode && state.capturing) demo.stop();
    updateStatusBar();
  });

  /* ── Capture start/stop ── */
  const btnCap   = document.getElementById('btn-capture');
  const capLabel = document.getElementById('capture-label');

  btnCap.addEventListener('click', () => {
    state.capturing = !state.capturing;

    if (state.capturing) {
      capLabel.textContent = '■ Stop';
      btnCap.classList.add('running');
      state.sampleCount    = 0;
      state.lastBatchTime  = performance.now();
      document.getElementById('no-data-overlay').classList.add('hidden');

      if (state.demoMode) {
        demo.onData = ingestData;
        demo.start();
      } else if (state.connected) {
        serial._sendCommand('START\n');
      }
    } else {
      capLabel.textContent = '▶ Capture';
      btnCap.classList.remove('running');
      if (state.demoMode) demo.stop();
      else if (state.connected) serial._sendCommand('STOP\n');
    }
    updateStatusBar();
  });

  /* ── USB connect ── */
  const btnConn   = document.getElementById('btn-connect');
  const connLabel = document.getElementById('connect-label');

  btnConn.addEventListener('click', async () => {
    if (state.connected) {
      await serial.disconnect();
    } else {
      if (!serial.isSupported) {
        alert('Web Serial API not supported.\nPlease use Chrome 89+ or Edge 89+.');
        return;
      }
      const ok = await serial.connect();
      if (ok) {
        state.demoMode = false;
        btnDemo.classList.remove('active');
        document.getElementById('hw-info').textContent = 'USB';
      }
    }
  });

  serial.onConnect = () => {
    state.connected  = true;
    serial.onData    = ingestData;
    connLabel.textContent = 'Disconnect';
    btnConn.classList.add('connected');
    updateStatusBar();
  };
  serial.onDisconnect = () => {
    state.connected = false;
    connLabel.textContent = 'Connect USB';
    btnConn.classList.remove('connected');
    updateStatusBar();
  };
  serial.onError = (msg) => alert('Serial error: ' + msg);

  /* ── Reset ── */
  document.getElementById('btn-reset').addEventListener('click', () => {
    if (state.capturing) {
      state.capturing = false;
      capLabel.textContent = '▶ Capture';
      btnCap.classList.remove('running');
      demo.stop();
    }
    demo.reset();
    store.timestamps.length = 0;
    for (let ch = 0; ch < 10; ch++) store.voltages[ch].length = 0;
    if (renderer) {
      renderer.cursor1T  = null;
      renderer.cursor2T  = null;
      renderer.following = true;
    }
    document.getElementById('no-data-overlay').classList.remove('hidden');
    updateSidebarValues();
    updateStatusBar();
  });

  /* ── Export PNG ── */
  document.getElementById('btn-export-png').addEventListener('click', () => {
    const url  = renderer.exportPNG();
    const link = document.createElement('a');
    link.href     = url;
    link.download = `vseq_${Date.now()}.png`;
    link.click();
  });

  /* ── Export CSV ── */
  document.getElementById('btn-export-csv').addEventListener('click', () => {
    if (store.timestamps.length === 0) { alert('No data to export.'); return; }
    const header = ['time_ms', ...state.channels.map(c => c.name)].join(',');
    const rows   = store.timestamps.map((t, i) =>
      [t.toFixed(3), ...store.voltages.map(v => (v[i] ?? 0).toFixed(4))].join(',')
    );
    const blob = new Blob([[header, ...rows].join('\n')], { type: 'text/csv' });
    const link = document.createElement('a');
    link.href     = URL.createObjectURL(blob);
    link.download = `vseq_${Date.now()}.csv`;
    link.click();
  });
}

/* ═══════════════════════════════════════════════════════
   ZOOM CONTROLS
═══════════════════════════════════════════════════════ */
function setupZoom() {
  const slider = document.getElementById('zoom-slider');

  const sliderToMs = (val) => 20 * Math.pow(3000, val / 100);

  slider.addEventListener('input', () => {
    if (renderer) renderer.viewWindow = Math.round(sliderToMs(parseFloat(slider.value)));
  });

  document.getElementById('btn-zoom-in').addEventListener('click', () => {
    if (renderer) renderer.viewWindow = Math.max(20, renderer.viewWindow * 0.7);
  });
  document.getElementById('btn-zoom-out').addEventListener('click', () => {
    if (renderer) renderer.viewWindow = Math.min(60000, renderer.viewWindow * 1.4);
  });
  document.getElementById('btn-follow').addEventListener('click', () => {
    if (renderer) renderer.following = true;
  });
  document.getElementById('btn-all-vis').addEventListener('click', () => {
    const anyHidden = state.channels.some(c => !c.visible);
    state.channels.forEach(c => {
      c.visible = anyHidden;
      document.getElementById(`ch-card-${c.index}`)
               .classList.toggle('hidden-ch', !c.visible);
    });
  });
}

/* ═══════════════════════════════════════════════════════
   TRIGGER LOGIC
═══════════════════════════════════════════════════════ */
let trigArmed     = false;
let trigLastState = false; // tracks prev sample above/below level

function setupTrigger() {
  document.getElementById('btn-arm').addEventListener('click', () => {
    trigArmed = !trigArmed;
    trigLastState = false;
    const btn     = document.getElementById('btn-arm');
    const stateEl = document.getElementById('trig-state');
    btn.classList.toggle('armed', trigArmed);
    stateEl.textContent = trigArmed ? 'ARMED' : 'STANDBY';
    stateEl.className   = 'trig-state' + (trigArmed ? ' armed' : '');
  });
}

function checkTrigger() {
  if (!trigArmed || !state.capturing) return;
  const chIdx = parseInt(document.getElementById('trig-ch').value);
  if (chIdx < 0) return;

  const edge   = document.getElementById('trig-edge').value;
  const level  = parseFloat(document.getElementById('trig-level').value);
  const samps  = store.voltages[chIdx];
  if (samps.length < 2) return;

  const len  = samps.length;
  const prev = samps[len - 2];
  const curr = samps[len - 1];
  const wasAbove = prev >= level;
  const isAbove  = curr >= level;

  let fired = false;
  if (edge === 'rising'  && !wasAbove && isAbove)  fired = true;
  if (edge === 'falling' &&  wasAbove && !isAbove) fired = true;
  if (edge === 'either'  && wasAbove !== isAbove)  fired = true;

  if (fired) {
    trigArmed = false;
    document.getElementById('btn-arm').classList.remove('armed');
    const st = document.getElementById('trig-state');
    st.textContent = 'TRIGGERED';
    st.className   = 'trig-state triggered';

    // Reposition view to trigger point
    if (renderer) {
      const trigT = store.timestamps[len - 1];
      renderer.following  = false;
      renderer.viewOffset = Math.max(0, trigT - renderer.viewWindow * 0.15);
    }
  }
}

/* ═══════════════════════════════════════════════════════
   RESIZE OBSERVER
═══════════════════════════════════════════════════════ */
function setupResize() {
  const ro = new ResizeObserver(() => {
    if (renderer) renderer.resize();
  });
  ro.observe(document.getElementById('waveform-wrap'));
}

/* ═══════════════════════════════════════════════════════
   INIT
═══════════════════════════════════════════════════════ */
function init() {
  // Build canvas renderer
  const canvas = document.getElementById('waveform-canvas');
  renderer = new WaveformRenderer(canvas);
  renderer.resize();

  // Wire cursor tooltip
  renderer.onCursorChange = (t, xPx, yPx) => showCursorTip(t, xPx, yPx);

  // Build UI
  buildSidebar();
  updateTriggerChannelSelect();
  setupToolbar();
  setupZoom();
  setupTrigger();
  setupResize();

  // Debug access
  window.vseq = { state, store, renderer, demo, serial };

  // Start render loop
  requestAnimationFrame(renderLoop);

  // Auto-start demo after a short delay
  setTimeout(() => {
    document.getElementById('btn-capture').click();
  }, 500);
}

// ES modules run deferred — DOM is already ready when this executes
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', init);
} else {
  init();
}
