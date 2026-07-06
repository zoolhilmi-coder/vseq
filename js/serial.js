/**
 * serial.js — Web Serial API wrapper
 *
 * Handles USB serial connection to the VSeq hardware (RP2040/Pico).
 * Data protocol (sent by firmware, one line per sample batch):
 *
 *   "<timestamp_ms>,<ch0_v>,<ch1_v>,...,<ch9_v>\n"
 *   e.g. "1234.5,12.003,4.998,3.302,0.000,0.000,...\n"
 *
 * Baud rate: 921600 (fast enough for 10ch × 1kSa/s)
 */

export class SerialManager {
  constructor() {
    this.port       = null;
    this.reader     = null;
    this.isOpen     = false;
    this._readLoop  = null;
    this._buf       = '';

    this.onData       = null;  // callback(timestamps[], voltages[][])
    this.onConnect    = null;  // callback()
    this.onDisconnect = null;  // callback()
    this.onError      = null;  // callback(msg)
  }

  get isSupported() {
    return 'serial' in navigator;
  }

  /**
   * Prompt the user to select a serial port and open it.
   */
  async connect() {
    if (!this.isSupported) {
      const msg = 'Web Serial API not supported.\nUse Chrome 89+ or Edge 89+.';
      if (this.onError) this.onError(msg);
      return false;
    }

    try {
      this.port = await navigator.serial.requestPort();
      await this.port.open({
        baudRate:   921600,
        dataBits:   8,
        stopBits:   1,
        parity:     'none',
        flowControl: 'none',
      });

      this.isOpen = true;
      if (this.onConnect) this.onConnect();

      // Send START command to firmware
      await this._sendCommand('START\n');

      // Begin reading
      this._startReadLoop();
      return true;

    } catch (err) {
      if (err.name !== 'NotFoundError') {
        if (this.onError) this.onError(`Connection failed: ${err.message}`);
      }
      return false;
    }
  }

  async disconnect() {
    if (!this.isOpen) return;

    try {
      await this._sendCommand('STOP\n');
    } catch (_) { /* ignore */ }

    try {
      if (this.reader) {
        await this.reader.cancel();
        this.reader = null;
      }
      await this.port.close();
    } catch (_) { /* ignore */ }

    this.isOpen = false;
    this.port   = null;
    this._buf   = '';

    if (this.onDisconnect) this.onDisconnect();
  }

  /**
   * Send a text command to the firmware
   */
  async _sendCommand(cmd) {
    if (!this.port || !this.port.writable) return;
    const writer = this.port.writable.getWriter();
    const enc    = new TextEncoder();
    await writer.write(enc.encode(cmd));
    writer.releaseLock();
  }

  /**
   * Continuously read lines from the serial port
   */
  _startReadLoop() {
    const dec = new TextDecoder();

    const readLoop = async () => {
      this.reader = this.port.readable.getReader();
      try {
        while (this.isOpen) {
          const { value, done } = await this.reader.read();
          if (done) break;

          this._buf += dec.decode(value, { stream: true });

          // Split on newlines and process complete lines
          const lines = this._buf.split('\n');
          this._buf = lines.pop(); // Keep incomplete line in buffer

          const timestamps = [];
          const voltages   = Array.from({ length: 10 }, () => []);
          let hadData = false;

          for (const line of lines) {
            const parsed = this._parseLine(line.trim());
            if (parsed) {
              timestamps.push(parsed.t);
              for (let ch = 0; ch < 10; ch++) {
                voltages[ch].push(parsed.v[ch] ?? 0);
              }
              hadData = true;
            }
          }

          if (hadData && this.onData) {
            this.onData(timestamps, voltages);
          }
        }
      } catch (err) {
        if (this.isOpen && this.onError) {
          this.onError(`Read error: ${err.message}`);
        }
      } finally {
        this.reader = null;
      }
    };

    this._readLoop = readLoop();
  }

  /**
   * Parse a data line: "timestamp_ms,v0,v1,...,v9"
   * Returns { t, v[] } or null on parse failure.
   */
  _parseLine(line) {
    if (!line || line.startsWith('#')) return null; // comments
    const parts = line.split(',');
    if (parts.length < 2) return null;

    const t = parseFloat(parts[0]);
    if (isNaN(t)) return null;

    const v = parts.slice(1).map(s => {
      const n = parseFloat(s);
      return isNaN(n) ? 0 : n;
    });

    return { t, v };
  }
}
