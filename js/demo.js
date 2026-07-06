/**
 * demo.js — GPU Power Sequence Simulator
 *
 * Simulates a realistic AMD GPU (RX 6800-style) power-on sequence
 * across 10 voltage rails. Runs as a timed data source that appends
 * samples to the shared data store at ~1kHz equivalent rate.
 */

export const CHANNEL_COLORS = [
  '#ff6b6b', // CH0 — red
  '#ff9f40', // CH1 — orange
  '#ffd23f', // CH2 — amber
  '#5cdb7f', // CH3 — green
  '#4db8ff', // CH4 — blue
  '#c77dff', // CH5 — purple
  '#ff79c6', // CH6 — pink
  '#a8f040', // CH7 — lime
  '#40e0d0', // CH8 — teal
  '#7b8cff', // CH9 — indigo
];

// Default channel names and voltage scales for GPU power probing
export const DEFAULT_CHANNELS = [
  { name: 'PWR_12V',    vMin: 0,    vMax: 14,   threshold: 11.0 },
  { name: 'PWR_5V',     vMin: 0,    vMax: 6,    threshold: 4.75 },
  { name: 'PWR_3V3',    vMin: 0,    vMax: 4,    threshold: 3.0  },
  { name: 'EN_VCORE',   vMin: 0,    vMax: 2.5,  threshold: 1.0  },
  { name: 'VCORE',      vMin: 0,    vMax: 1.5,  threshold: 0.85 },
  { name: 'VRAM',       vMin: 0,    vMax: 1.8,  threshold: 1.2  },
  { name: 'VDDCI',      vMin: 0,    vMax: 1.5,  threshold: 0.75 },
  { name: 'MVDD',       vMin: 0,    vMax: 2.5,  threshold: 1.6  },
  { name: 'PGOOD',      vMin: 0,    vMax: 4,    threshold: 2.5  },
  { name: 'VSOC',       vMin: 0,    vMax: 1.2,  threshold: 0.65 },
];

// Sequence: target voltage and rise-time offset for each rail (ms after trigger)
const SEQUENCE = [
  { targetV: 12.00, riseAt:  15, riseMs: 8  },  // CH0: 12V main rail
  { targetV:  5.00, riseAt:  28, riseMs: 6  },  // CH1: 5V rail
  { targetV:  3.30, riseAt:  40, riseMs: 5  },  // CH2: 3.3V rail
  { targetV:  1.80, riseAt:  60, riseMs: 3  },  // CH3: EN_VCORE (fast enable)
  { targetV:  1.00, riseAt:  72, riseMs: 8  },  // CH4: VCORE (ramps slowly)
  { targetV:  1.35, riseAt:  92, riseMs: 5  },  // CH5: VRAM
  { targetV:  0.90, riseAt: 105, riseMs: 4  },  // CH6: VDDCI
  { targetV:  1.80, riseAt: 112, riseMs: 4  },  // CH7: MVDD
  { targetV:  3.30, riseAt: 128, riseMs: 2  },  // CH8: PGOOD (sharp pulse)
  { targetV:  0.75, riseAt: 145, riseMs: 6  },  // CH9: VSOC
];

const CYCLE_MS   = 3000; // repeat demo cycle every 3 seconds
const SAMPLE_MS  = 1;    // 1ms per sample = 1kSa/s per channel
const BATCH_MS   = 16;   // generate ~16ms of data per animation frame

/**
 * Smooth sigmoid rise function
 * @param {number} t - current time (ms)
 * @param {number} riseAt - rise start time (ms)
 * @param {number} riseMs - rise duration (ms)
 */
function sigmoid(t, riseAt, riseMs) {
  if (t < riseAt) return 0;
  const x = (t - riseAt) / riseMs;
  if (x >= 1) return 1;
  // Cubic ease-in-out
  return x < 0.5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2;
}

/**
 * Generate a single voltage sample for channel i at time t (ms in cycle)
 */
function sampleVoltage(chIdx, cycleTms) {
  const seq = SEQUENCE[chIdx];
  const level = sigmoid(cycleTms, seq.riseAt, seq.riseMs);
  const v = seq.targetV * level;

  // Add realistic noise only when rail is active
  if (level > 0.02) {
    const noise   = (Math.random() - 0.5) * 0.008 * seq.targetV;
    const ripple  = Math.sin(cycleTms * 0.314) * 0.004 * seq.targetV;
    return v + noise + ripple;
  }
  // Sub-threshold noise floor
  return Math.random() * 0.008;
}

export class DemoGenerator {
  constructor() {
    this._running   = false;
    this._rafId     = null;
    this._startWall = null;   // performance.now() at capture start
    this._headMs    = 0;      // leading edge of generated data (ms)
    this.onData     = null;   // callback(timestamps[], voltages[][])
  }

  start() {
    if (this._running) return;
    this._running   = true;
    this._startWall = performance.now();
    this._headMs    = 0;
    this._tick();
  }

  stop() {
    this._running = false;
    if (this._rafId) {
      cancelAnimationFrame(this._rafId);
      this._rafId = null;
    }
  }

  reset() {
    this.stop();
    this._headMs = 0;
    this._startWall = null;
  }

  _tick = () => {
    if (!this._running) return;

    const wallElapsed = performance.now() - this._startWall;
    const targetHead  = wallElapsed; // real-time: generate up to now

    const timestamps = [];
    const voltages   = Array.from({ length: 10 }, () => []);

    // Generate all samples we're "behind" on
    while (this._headMs < targetHead) {
      const t = this._headMs;
      const cycleTms = t % CYCLE_MS;

      timestamps.push(t);
      for (let ch = 0; ch < 10; ch++) {
        voltages[ch].push(sampleVoltage(ch, cycleTms));
      }

      this._headMs += SAMPLE_MS;
    }

    if (timestamps.length > 0 && this.onData) {
      this.onData(timestamps, voltages);
    }

    this._rafId = requestAnimationFrame(this._tick);
  };
}
