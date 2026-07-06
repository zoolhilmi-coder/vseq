/**
 * renderer.js — Canvas Waveform Renderer
 *
 * Renders all 10 channels as stacked, colour-coded waveforms on an
 * HTML canvas.  Handles HiDPI, zoom, pan, hover cursors, and threshold
 * lines.  Inspired by the visual language of PicoScope / Saleae Logic.
 *
 * Layout (horizontal, px):
 *   [LEFT_M]  voltage-axis labels
 *   [plotW ]  waveform
 *   [RIGHT_M] current-value readout
 *
 * Layout (vertical, per strip):
 *   [TIME_H] time axis at bottom
 *   [chH * N] stacked channel strips
 */

const LEFT_M   = 60;
const RIGHT_M  = 80;
const TIME_H   = 34;
const STRIP_PY = 6;   // strip top/bottom padding

export class WaveformRenderer {
  /**
   * @param {HTMLCanvasElement} canvas
   */
  constructor(canvas) {
    this.canvas = canvas;
    this.ctx    = canvas.getContext('2d', { alpha: false });
    this.dpr    = Math.min(window.devicePixelRatio || 1, 2);

    // View state
    this.viewWindow  = 500;   // ms visible at once
    this.viewOffset  = 0;     // ms: left-edge timestamp
    this.following   = true;  // auto-scroll to latest

    // Cursor state
    this.hoverX      = null;  // px on canvas (logical)
    this.cursor1T    = null;  // ms timestamp
    this.cursor2T    = null;  // ms timestamp
    this.cursorMode  = 1;     // which cursor dragging sets (1 or 2)

    // Interaction
    this._dragging   = false;
    this._dragStartX = 0;
    this._dragOffset = 0;

    // Callbacks
    this.onViewChange   = null;  // () => void
    this.onCursorChange = null;  // (c1T, c2T, xPx, channels) => void

    this._bindEvents();
  }

  /* ────────────────── Public API ────────────────── */

  resize() {
    const p = this.canvas.parentElement;
    const w = p.clientWidth;
    const h = p.clientHeight;
    this.canvas.width  = Math.round(w * this.dpr);
    this.canvas.height = Math.round(h * this.dpr);
    this.canvas.style.width  = w + 'px';
    this.canvas.style.height = h + 'px';
  }

  /**
   * Main render call — call inside requestAnimationFrame
   * @param {object} state  — see app.js for shape
   */
  render(state) {
    const { channels, timestamps, voltages } = state;
    const ctx = this.ctx;
    const dpr = this.dpr;
    const CW  = this.canvas.width  / dpr;
    const CH  = this.canvas.height / dpr;

    ctx.save();
    ctx.scale(dpr, dpr);

    /* Background */
    ctx.fillStyle = '#060a0e';
    ctx.fillRect(0, 0, CW, CH);

    const plotW  = CW - LEFT_M - RIGHT_M;
    const plotH  = CH - TIME_H;
    const nCh    = channels.length;
    const chH    = plotH / nCh;

    /* Compute view range */
    let viewStart, viewEnd;
    const latest = timestamps.length ? timestamps[timestamps.length - 1] : 0;
    if (this.following) {
      viewEnd   = Math.max(latest, this.viewWindow);
      viewStart = viewEnd - this.viewWindow;
    } else {
      viewStart = this.viewOffset;
      viewEnd   = viewStart + this.viewWindow;
    }

    // Store for interaction queries
    this._viewStart = viewStart;
    this._viewEnd   = viewEnd;
    this._plotW     = plotW;
    this._chH       = chH;
    this._nCh       = nCh;
    this._CH        = CH;

    /* ── Draw each channel strip ── */
    const visible = channels.filter(c => c.visible);
    for (let i = 0; i < nCh; i++) {
      const ch   = channels[i];
      const stripY = i * chH;
      this._drawStrip(ctx, ch, voltages[ch.index], timestamps,
                      stripY, chH, CW, plotW, viewStart, viewEnd);
    }

    /* ── Strip separators ── */
    ctx.strokeStyle = 'rgba(255,255,255,0.05)';
    ctx.lineWidth   = 1;
    for (let i = 1; i < nCh; i++) {
      const y = Math.round(i * chH) + 0.5;
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(CW, y);
      ctx.stroke();
    }

    /* ── Left margin border ── */
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(LEFT_M + 0.5, 0);
    ctx.lineTo(LEFT_M + 0.5, plotH);
    ctx.stroke();

    /* ── Right margin border ── */
    ctx.beginPath();
    ctx.moveTo(CW - RIGHT_M + 0.5, 0);
    ctx.lineTo(CW - RIGHT_M + 0.5, plotH);
    ctx.stroke();

    /* ── Time axis ── */
    this._drawTimeAxis(ctx, CW, CH, plotW, viewStart, viewEnd);

    /* ── Hover cursor ── */
    if (this.hoverX !== null) {
      const x = this.hoverX;
      ctx.strokeStyle = 'rgba(255,255,255,0.25)';
      ctx.lineWidth   = 1;
      ctx.setLineDash([3, 5]);
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, plotH);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    /* ── Measurement cursors ── */
    if (this.cursor1T !== null) {
      const x = this._t2x(this.cursor1T, viewStart, viewEnd, plotW);
      this._drawMeasCursor(ctx, x, plotH, '#ffffff', '1');
    }
    if (this.cursor2T !== null) {
      const x = this._t2x(this.cursor2T, viewStart, viewEnd, plotW);
      this._drawMeasCursor(ctx, x, plotH, '#ffd23f', '2');
    }

    ctx.restore();
  }

  /* ────────────────── Drawing helpers ────────────────── */

  _drawStrip(ctx, ch, samples, timestamps, y, h, CW, plotW, viewStart, viewEnd) {
    const innerH = h - STRIP_PY * 2;
    const innerY = y + STRIP_PY;
    const vRange = ch.vMax - ch.vMin;

    const t2x = (t) => this._t2x(t, viewStart, viewEnd, plotW);
    const v2y = (v) => {
      const clamped = Math.max(ch.vMin, Math.min(ch.vMax, v));
      return innerY + innerH - ((clamped - ch.vMin) / vRange) * innerH;
    };

    /* ── Channel background (subtle) ── */
    const bgAlpha = ch.highlighted ? '0a' : '05';
    ctx.fillStyle = ch.color + bgAlpha;
    ctx.fillRect(LEFT_M + 1, y + 1, plotW - 1, h - 2);

    /* ── Voltage grid lines ── */
    const nGridV = 4;
    ctx.font      = '9px JetBrains Mono, monospace';
    ctx.textAlign = 'right';

    for (let j = 0; j <= nGridV; j++) {
      const fraction = j / nGridV;
      const gy = innerY + fraction * innerH;
      const gv = ch.vMax - fraction * vRange;

      // Gridline
      ctx.strokeStyle = 'rgba(255,255,255,0.05)';
      ctx.lineWidth   = 0.5;
      ctx.setLineDash([3, 4]);
      ctx.beginPath();
      ctx.moveTo(LEFT_M + 1, gy);
      ctx.lineTo(LEFT_M + plotW, gy);
      ctx.stroke();
      ctx.setLineDash([]);

      // Voltage label (only top, mid, bottom)
      if (j === 0 || j === nGridV / 2 || j === nGridV) {
        ctx.fillStyle = 'rgba(255,255,255,0.22)';
        ctx.fillText(gv.toFixed(gv < 2 ? 2 : 1) + 'V', LEFT_M - 4, gy + 3.5);
      }
    }

    /* ── Threshold line ── */
    if (ch.threshold !== null && ch.threshold > ch.vMin && ch.threshold < ch.vMax) {
      const ty = v2y(ch.threshold);
      ctx.strokeStyle = ch.color + '55';
      ctx.lineWidth   = 1;
      ctx.setLineDash([6, 5]);
      ctx.beginPath();
      ctx.moveTo(LEFT_M, ty);
      ctx.lineTo(LEFT_M + plotW, ty);
      ctx.stroke();
      ctx.setLineDash([]);

      // Threshold label
      ctx.fillStyle   = ch.color + '88';
      ctx.font        = '9px JetBrains Mono, monospace';
      ctx.textAlign   = 'left';
      ctx.fillText(ch.threshold.toFixed(2) + 'V', LEFT_M + 4, ty - 3);
    }

    /* ── Channel ID in left margin ── */
    ctx.fillStyle = ch.color;
    ctx.font      = '700 10px Inter, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText(`CH${ch.index}`, 4, y + 14);

    ctx.fillStyle = 'rgba(255,255,255,0.3)';
    ctx.font      = '10px Inter, sans-serif';
    const nameSlice = ch.name.length > 7 ? ch.name.slice(0, 7) + '…' : ch.name;
    ctx.fillText(nameSlice, 4, y + 26);

    /* ── Waveform ── */
    if (!samples || samples.length === 0) {
      // Flat 0V line
      const flatY = v2y(0);
      ctx.strokeStyle = ch.color + '30';
      ctx.lineWidth   = 1;
      ctx.beginPath();
      ctx.moveTo(LEFT_M, flatY);
      ctx.lineTo(LEFT_M + plotW, flatY);
      ctx.stroke();
    } else {
      // Find visible index range via binary search
      const startIdx = Math.max(0, this._bisectLeft(timestamps, viewStart) - 1);
      const endIdx   = Math.min(timestamps.length - 1,
                                this._bisectRight(timestamps, viewEnd) + 1);

      if (endIdx >= startIdx) {
        // ── Area fill ──
        const grad = ctx.createLinearGradient(0, innerY, 0, innerY + innerH);
        grad.addColorStop(0, ch.color + '28');
        grad.addColorStop(1, ch.color + '00');

        ctx.beginPath();
        let px = t2x(timestamps[startIdx]);
        let py = v2y(samples[startIdx]);
        ctx.moveTo(px, v2y(0));
        ctx.lineTo(px, py);

        for (let i = startIdx + 1; i <= endIdx; i++) {
          const nx = t2x(timestamps[i]);
          const ny = v2y(samples[i]);
          // Skip points that map to same pixel (LOD optimisation)
          if (nx - px < 0.4 && i < endIdx) continue;
          ctx.lineTo(nx, ny);
          px = nx; py = ny;
        }

        ctx.lineTo(t2x(timestamps[endIdx]), v2y(0));
        ctx.closePath();
        ctx.fillStyle = grad;
        ctx.fill();

        // ── Waveform line ──
        ctx.beginPath();
        px = t2x(timestamps[startIdx]);
        py = v2y(samples[startIdx]);
        ctx.moveTo(px, py);

        for (let i = startIdx + 1; i <= endIdx; i++) {
          const nx = t2x(timestamps[i]);
          const ny = v2y(samples[i]);
          if (nx - px < 0.4 && i < endIdx) continue;
          ctx.lineTo(nx, ny);
          px = nx; py = ny;
        }

        ctx.strokeStyle = ch.color;
        ctx.lineWidth   = 1.8;
        ctx.lineJoin    = 'round';
        ctx.lineCap     = 'round';

        // Glow pass
        ctx.shadowColor = ch.color;
        ctx.shadowBlur  = 4;
        ctx.stroke();
        ctx.shadowBlur  = 0;
      }
    }

    /* ── Current value (right margin) ── */
    const lastV  = samples && samples.length > 0 ? samples[samples.length - 1] : null;
    const dispV  = lastV !== null ? lastV.toFixed(3) + 'V' : '—';
    const valY   = y + h / 2 + 5;

    ctx.fillStyle = lastV !== null ? ch.color : 'rgba(255,255,255,0.15)';
    ctx.font      = '700 13px JetBrains Mono, monospace';
    ctx.textAlign = 'left';
    ctx.fillText(dispV, CW - RIGHT_M + 8, valY);

    // Min / max (small)
    if (samples && samples.length > 0) {
      let mn = Infinity, mx = -Infinity;
      const scanFrom = Math.max(0, samples.length - 2000);
      for (let i = scanFrom; i < samples.length; i++) {
        if (samples[i] < mn) mn = samples[i];
        if (samples[i] > mx) mx = samples[i];
      }
      ctx.fillStyle = 'rgba(255,255,255,0.2)';
      ctx.font      = '9px JetBrains Mono, monospace';
      ctx.fillText(`↑${mx.toFixed(2)}`, CW - RIGHT_M + 8, valY + 13);
      ctx.fillText(`↓${mn.toFixed(2)}`, CW - RIGHT_M + 8, valY + 23);
    }
  }

  _drawTimeAxis(ctx, CW, CH, plotW, viewStart, viewEnd) {
    const axisY = CH - TIME_H;

    ctx.fillStyle = '#0c1118';
    ctx.fillRect(0, axisY, CW, TIME_H);

    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.lineWidth   = 1;
    ctx.beginPath();
    ctx.moveTo(0, axisY + 0.5);
    ctx.lineTo(CW, axisY + 0.5);
    ctx.stroke();

    const nDivs = 10;
    for (let i = 0; i <= nDivs; i++) {
      const frac = i / nDivs;
      const t    = viewStart + frac * (viewEnd - viewStart);
      const x    = LEFT_M + frac * plotW;

      // Major tick
      ctx.strokeStyle = 'rgba(255,255,255,0.18)';
      ctx.lineWidth   = 1;
      ctx.beginPath();
      ctx.moveTo(x, axisY);
      ctx.lineTo(x, axisY + 6);
      ctx.stroke();

      // Vertical grid line (subtle)
      ctx.strokeStyle = 'rgba(255,255,255,0.04)';
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, axisY);
      ctx.stroke();

      // Time label
      ctx.fillStyle  = 'rgba(255,255,255,0.35)';
      ctx.font       = '10px JetBrains Mono, monospace';
      ctx.textAlign  = 'center';
      ctx.fillText(formatTime(t), x, axisY + 22);
    }
  }

  _drawMeasCursor(ctx, x, plotH, color, label) {
    ctx.strokeStyle = color + 'cc';
    ctx.lineWidth   = 1.5;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(x, 0);
    ctx.lineTo(x, plotH);
    ctx.stroke();
    ctx.setLineDash([]);

    // Label badge
    ctx.fillStyle    = color;
    ctx.font         = 'bold 10px JetBrains Mono, monospace';
    ctx.textAlign    = 'center';
    const badge      = ' C' + label + ' ';
    const bW         = ctx.measureText(badge).width + 4;
    ctx.fillRect(x - bW / 2, 4, bW, 16);
    ctx.fillStyle = '#060a0e';
    ctx.fillText(badge, x, 15);
  }

  /* ────────────────── Utilities ────────────────── */

  _t2x(t, viewStart, viewEnd, plotW) {
    return LEFT_M + ((t - viewStart) / (viewEnd - viewStart)) * plotW;
  }

  _x2t(x, viewStart, viewEnd, plotW) {
    return viewStart + ((x - LEFT_M) / plotW) * (viewEnd - viewStart);
  }

  _bisectLeft(arr, val) {
    let lo = 0, hi = arr.length;
    while (lo < hi) {
      const mid = (lo + hi) >>> 1;
      if (arr[mid] < val) lo = mid + 1; else hi = mid;
    }
    return lo;
  }

  _bisectRight(arr, val) {
    let lo = 0, hi = arr.length;
    while (lo < hi) {
      const mid = (lo + hi) >>> 1;
      if (arr[mid] <= val) lo = mid + 1; else hi = mid;
    }
    return lo;
  }

  /* ────────────────── Interaction ────────────────── */

  _bindEvents() {
    const c = this.canvas;

    /* Zoom via scroll wheel */
    c.addEventListener('wheel', (e) => {
      e.preventDefault();
      const factor = e.deltaY > 0 ? 1.25 : 0.8;
      this.viewWindow = Math.max(20, Math.min(60000, this.viewWindow * factor));

      // Zoom towards mouse position
      const rect   = c.getBoundingClientRect();
      const mx     = e.clientX - rect.left;
      const frac   = (mx - LEFT_M) / (c.clientWidth - LEFT_M - RIGHT_M);
      const pivotT = this._viewStart + frac * (this._viewEnd - this._viewStart);

      if (!this.following) {
        this.viewOffset = pivotT - frac * this.viewWindow;
        this.viewOffset = Math.max(0, this.viewOffset);
      }
      if (this.onViewChange) this.onViewChange();
    }, { passive: false });

    /* Pan via drag */
    c.addEventListener('mousedown', (e) => {
      if (e.button !== 0) return;
      this._dragging    = true;
      this._dragStartX  = e.clientX;
      this._dragOffset  = this.viewOffset;
      this.following    = false;
      if (this.onViewChange) this.onViewChange(); // update follow button
      c.style.cursor = 'grabbing';
    });

    c.addEventListener('mousemove', (e) => {
      const rect = c.getBoundingClientRect();
      const x    = e.clientX - rect.left;

      if (this._dragging) {
        const dx    = e.clientX - this._dragStartX;
        const dT    = (dx / (c.clientWidth - LEFT_M - RIGHT_M)) * this.viewWindow;
        this.viewOffset = Math.max(0, this._dragOffset - dT);
        if (this.onViewChange) this.onViewChange();
      }

      // Hover cursor + tooltip
      if (x > LEFT_M && x < c.clientWidth - RIGHT_M) {
        this.hoverX = x;
      } else {
        this.hoverX = null;
      }

      if (this.onCursorChange) {
        const t = this._x2t(x, this._viewStart, this._viewEnd,
                            c.clientWidth - LEFT_M - RIGHT_M);
        this.onCursorChange(t, x, e.clientY);
      }
    });

    c.addEventListener('mouseup',    () => { this._dragging = false; c.style.cursor = 'crosshair'; });
    c.addEventListener('mouseleave', () => {
      this._dragging = false;
      this.hoverX    = null;
      c.style.cursor = 'default';
      if (this.onCursorChange) this.onCursorChange(null, null, null);
    });

    /* Double-click: re-enable follow */
    c.addEventListener('dblclick', () => {
      this.following = true;
      if (this.onViewChange) this.onViewChange();
    });

    /* Right-click: set measurement cursors */
    c.addEventListener('contextmenu', (e) => {
      e.preventDefault();
      const rect = c.getBoundingClientRect();
      const x    = e.clientX - rect.left;
      const t    = this._x2t(x, this._viewStart, this._viewEnd,
                             c.clientWidth - LEFT_M - RIGHT_M);
      if (this.cursorMode === 1) {
        this.cursor1T   = t;
        this.cursorMode = 2;
      } else {
        this.cursor2T   = t;
        this.cursorMode = 1;
      }
      if (this.onViewChange) this.onViewChange();
    });
  }

  /**
   * Export the current canvas frame as a PNG data URL
   */
  exportPNG() {
    return this.canvas.toDataURL('image/png');
  }

  /**
   * Interpolate channel voltage at a given timestamp
   */
  valueAtTime(samples, timestamps, t) {
    if (!samples || samples.length === 0) return null;
    const idx = this._bisectLeft(timestamps, t);
    if (idx <= 0) return samples[0];
    if (idx >= samples.length) return samples[samples.length - 1];
    // Linear interpolation
    const t0 = timestamps[idx - 1], t1 = timestamps[idx];
    const v0 = samples[idx - 1],    v1 = samples[idx];
    const frac = (t - t0) / (t1 - t0);
    return v0 + frac * (v1 - v0);
  }
}

/* ─── Formatting helpers ─── */
function formatTime(ms) {
  if (ms < 0)       return '-' + formatTime(-ms);
  if (ms < 1000)    return ms.toFixed(0) + 'ms';
  if (ms < 10000)   return (ms / 1000).toFixed(2) + 's';
  return (ms / 1000).toFixed(1) + 's';
}
