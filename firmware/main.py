"""
VSeq Firmware — main.py
Raspberry Pi Pico (RP2040) / MicroPython

Reads 10 ADC channels and streams voltage data over USB serial.
- CH0–CH2 : RP2040 built-in ADC (GP26, GP27, GP28) — 0-3.3V
- CH3–CH9 : Two MCP3204 chips via SPI (4 ch each) — 0-3.3V

Data line format (one line per sample set):
  "<timestamp_ms>,<v0>,<v1>,...,<v9>\n"
  e.g. "1234.500,12.003,4.998,3.301,1.800,1.000,1.351,0.900,1.800,3.298,0.751"

Voltage divider ratios per channel are configured here.
For channels probing >3.3V rails, set SCALE_FACTOR accordingly.
"""

import machine
import utime
import sys

# ─── Configuration ─────────────────────────────────────────
BAUD_RATE    = 921600
SAMPLE_RATE  = 1000    # Hz — samples per second per channel

# Voltage scale factors (hardware voltage divider ratios)
# e.g. 12V rail: R1=39k, R2=12k → ratio = (39+12)/12 = 4.25
SCALE_FACTORS = [
    4.25,   # CH0 — 12V  rail  (R:39k/12k)
    1.65,   # CH1 — 5V   rail  (R:20k/22k)
    1.0,    # CH2 — 3.3V rail  (direct)
    1.0,    # CH3 — EN   signal (direct ≤3.3V)
    1.0,    # CH4 — VCORE      (direct ≤3.3V)
    1.0,    # CH5 — VRAM       (direct ≤3.3V)
    1.0,    # CH6 — VDDCI      (direct ≤3.3V)
    1.0,    # CH7 — MVDD       (direct ≤3.3V)
    1.0,    # CH8 — PGOOD      (direct ≤3.3V)
    1.0,    # CH9 — VSOC       (direct ≤3.3V)
]

ADC_VREF = 3.3    # Reference voltage
ADC_BITS = 12     # MCP3204 is 12-bit; RP2040 ADC is 12-bit effective

# ─── SPI / MCP3204 setup ────────────────────────────────────
# MCP3204A: channels 3–6  (CS = GP5)
# MCP3204B: channels 7–9  (CS = GP9) — only 3 of 4 used
SPI_ID   = 0
SPI_SCK  = machine.Pin(2)
SPI_MOSI = machine.Pin(3)
SPI_MISO = machine.Pin(4)
CS_A     = machine.Pin(5,  machine.Pin.OUT, value=1)
CS_B     = machine.Pin(9,  machine.Pin.OUT, value=1)

spi = machine.SPI(SPI_ID,
                  baudrate=1_000_000,
                  polarity=0,
                  phase=0,
                  bits=8,
                  sck=SPI_SCK,
                  mosi=SPI_MOSI,
                  miso=SPI_MISO)

# ─── Internal ADC (CH0–CH2) ──────────────────────────────────
adc0 = machine.ADC(machine.Pin(26))   # CH0
adc1 = machine.ADC(machine.Pin(27))   # CH1
adc2 = machine.ADC(machine.Pin(28))   # CH2
internal_adcs = [adc0, adc1, adc2]

# ─── MCP3204 read ────────────────────────────────────────────
def mcp3204_read(cs_pin, channel):
    """Read one channel (0-3) from MCP3204.  Returns 12-bit integer."""
    # Start bit + SGL/DIFF (1=single) + D2 + D1 + D0
    start   = 0b00000110  | ((channel >> 2) & 1)
    cfg     = (channel & 0x03) << 6
    buf_tx  = bytearray([start, cfg, 0x00])
    buf_rx  = bytearray(3)
    cs_pin.value(0)
    spi.write_readinto(buf_tx, buf_rx)
    cs_pin.value(1)
    return ((buf_rx[1] & 0x0F) << 8) | buf_rx[2]

def read_all_channels():
    """Return list of 10 voltages (float, V)."""
    readings = []
    # Internal ADC: CH0–CH2
    for adc in internal_adcs:
        raw = adc.read_u16() >> 4   # 16-bit → 12-bit
        v   = (raw / 4095.0) * ADC_VREF
        readings.append(v)
    # MCP3204 A: CH3–CH6
    for ch in range(4):
        raw = mcp3204_read(CS_A, ch)
        v   = (raw / 4095.0) * ADC_VREF
        readings.append(v)
    # MCP3204 B: CH7–CH9
    for ch in range(3):
        raw = mcp3204_read(CS_B, ch)
        v   = (raw / 4095.0) * ADC_VREF
        readings.append(v)
    # Apply scale factors
    return [readings[i] * SCALE_FACTORS[i] for i in range(10)]

# ─── Command parser ───────────────────────────────────────────
running    = False
sample_us  = 1_000_000 // SAMPLE_RATE   # microseconds per sample
t0_ms      = utime.ticks_ms()

def handle_command(cmd):
    global running, sample_us
    cmd = cmd.strip()
    if cmd == 'START':
        running = True
    elif cmd == 'STOP':
        running = False
    elif cmd.startswith('RATE:'):
        try:
            hz = int(cmd[5:])
            sample_us = 1_000_000 // max(1, min(5000, hz))
        except:
            pass
    elif cmd == 'ID?':
        sys.stdout.write('# VSeq v1.0 RP2040 10ch\n')

# ─── Main loop ───────────────────────────────────────────────
print('# VSeq v1.0 — send START to begin\n')

buf_in = ''
next_t = utime.ticks_us()

while True:
    # Non-blocking command read
    try:
        while sys.stdin.readable():   # type: ignore[attr-defined]
            ch = sys.stdin.read(1)
            if not ch:
                break
            buf_in += ch
            if '\n' in buf_in:
                line, buf_in = buf_in.split('\n', 1)
                handle_command(line)
    except:
        pass

    if not running:
        utime.sleep_ms(10)
        continue

    # Rate-limited sampling
    now = utime.ticks_us()
    if utime.ticks_diff(next_t, now) > 0:
        utime.sleep_us(utime.ticks_diff(next_t, now))
    next_t = utime.ticks_add(now, sample_us)

    t_ms    = utime.ticks_diff(utime.ticks_ms(), t0_ms)
    voltages = read_all_channels()

    # Format: "timestamp_ms,v0,v1,...,v9\n"
    line = '{:.3f},{}\n'.format(
        t_ms,
        ','.join('{:.4f}'.format(v) for v in voltages)
    )
    sys.stdout.write(line)
