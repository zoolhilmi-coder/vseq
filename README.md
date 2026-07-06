# VSeq — Voltage Sequence Analyzer

Multi-channel voltage monitor dengan paparan ala logic analyzer / oscilloscope. Sesuai untuk debug power sequencing pada GPU, motherboard, atau mana-mana PCB.

---

## 🖥️ PC Software (Guna Sekarang — Tanpa Hardware)

### Demo Mode
```
Buka index.html dalam Chrome atau Edge
→ Demo Mode auto-start — akan simulate GPU power sequence
```

**Requirements:**  
Chrome 89+ atau Edge 89+ (untuk Web Serial API)

### Features
| Feature | Cara Guna |
|---------|-----------|
| **Zoom** | Scroll mouse pada waveform |
| **Pan** | Drag kiri-kanan |
| **Follow latest** | Double-click atau klik ⟫ Follow |
| **Cursor** | Right-click letak cursor (C1/C2) |
| **Tooltip** | Hover untuk baca nilai semua channel |
| **Trigger** | Set channel + threshold + ARM |
| **Rename channel** | Double-click nama channel di sidebar |
| **Hide/show** | Klik 👁 pada channel |
| **Export PNG** | Toolbar → PNG |
| **Export CSV** | Toolbar → CSV |

---

## ⚡ Hardware — RP2040 (Raspberry Pi Pico)

### Bill of Materials

| Qty | Part | Value | Notes |
|-----|------|-------|-------|
| 1 | Raspberry Pi Pico | — | RP2040, USB built-in |
| 2 | MCP3204-CI/P | 12-bit ADC | SPI, 4ch each |
| 10 | Resistor | 100Ω | Input series resistor |
| 10 | Zener diode | 3.3V | Input clamp protection |
| 10 | Test probe / pogo pin | — | For probing PCB |
| Varies | Voltage divider R | See table | Scale high voltages |

### Voltage Divider Values per Rail

| Rail | Voltage | R1 | R2 | Scale |
|------|---------|----|----|-------|
| 12V  | 12V | 39kΩ | 12kΩ | 4.25x |
| 5V   | 5V  | 20kΩ | 22kΩ | 1.91x |
| 3.3V | 3.3V | Direct | — | 1.0x |
| EN, VCORE, VRAM, etc. | ≤3.3V | Direct | — | 1.0x |

> **⚠️ Warning:** Jangan probe mana-mana voltage melebihi 3.3V tanpa voltage divider + Zener clamp. RP2040 ADC toleran max 3.3V.

---

## 🔌 Wiring Diagram

```
Pico GPIO   Function
─────────────────────────────────────────
GP26  ──►  CH0 ADC input  (internal ADC0)
GP27  ──►  CH1 ADC input  (internal ADC1)
GP28  ──►  CH2 ADC input  (internal ADC2)

GP2   ──►  SPI0 SCK  (MCP3204 A & B)
GP3   ──►  SPI0 MOSI (MCP3204 A & B)
GP4   ──►  SPI0 MISO (MCP3204 A & B)
GP5   ──►  CS_A (MCP3204 A → CH3–CH6)
GP9   ──►  CS_B (MCP3204 B → CH7–CH9)

3V3   ──►  VDD  (MCP3204 power + VREF)
GND   ──►  VSS  (common ground)
VBUS  ──►  USB  (PC connection)
```

### MCP3204 Pinout (each chip)

```
MCP3204 A (CH3–CH6):
  CH0/IN0 → Probe CH3
  CH1/IN1 → Probe CH4
  CH2/IN2 → Probe CH5
  CH3/IN3 → Probe CH6

MCP3204 B (CH7–CH9):
  CH0/IN0 → Probe CH7
  CH1/IN1 → Probe CH8
  CH2/IN2 → Probe CH9
  CH3/IN3 → (spare / GND)
```

### Per-channel input circuit

```
Probe tip
   │
  [100Ω]    ← Series protection resistor
   │
   ├──[Zener 3.3V]── GND  ← Clamp overvoltage
   │
  [R1]      ← Voltage divider (for >3.3V rails)
   │
  [R2]      ← To GND
   │
  ADC pin
```

---

## 💾 Flash Firmware

1. Download **MicroPython UF2** dari [micropython.org/download/rp2-pico](https://micropython.org/download/rp2-pico/)
2. Hold BOOTSEL → plug USB → release
3. Drag UF2 ke drive `RPI-RP2`
4. Copy `firmware/main.py` ke Pico menggunakan **Thonny** atau **rshell**:

```bash
# Via rshell
pip install rshell
rshell --port /dev/tty.usbmodem* cp firmware/main.py /pyboard/main.py
```

5. Reset Pico
6. Buka VSeq PC app → **Connect USB** → pilih port Pico

---

## 📡 Serial Protocol

```
# PC → Pico (commands)
START           Start streaming data
STOP            Stop streaming
RATE:1000       Set sample rate (Sa/s), max 5000
ID?             Query device identity

# Pico → PC (data)
# VSeq v1.0 RP2040 10ch         (startup message)
1234.500,12.003,4.998,...       (CSV: time_ms, v0..v9)
```

---

## 📊 Performance

| Parameter | Value |
|-----------|-------|
| ADC resolution | 12-bit (4096 steps) |
| Voltage resolution | ~0.8 mV @ 3.3V |
| Max sample rate | ~5 kSa/s (shared, USB bandwidth limited) |
| Channels | 10 (3 internal + 7 via SPI ADC) |
| Input range | 0–3.3V (hardware protected) |
| Supported rails | Up to 12V (with divider) |
| USB mode | CDC Serial — no driver needed |

---

## 🔧 Troubleshooting

**"No data" in app:**
- Pastikan klik **▶ Capture** lepas connect
- Check baud rate: 921600 bps

**Noisy readings:**
- Tambah 100nF ceramic cap antara ADC pin dan GND
- Pastikan ground probe disambung ke PCB GND yang sama

**Wrong voltage reading:**
- Semak `SCALE_FACTORS` dalam `firmware/main.py`
- Match dengan voltage divider yang kau guna

---

## 📁 Project Structure

```
vseq/
├── index.html          ← PC Web App
├── style.css           ← Dark oscilloscope theme
├── js/
│   ├── app.js          ← Main orchestrator
│   ├── renderer.js     ← Canvas waveform engine
│   ├── serial.js       ← Web Serial API wrapper
│   └── demo.js         ← GPU power sequence simulator
├── firmware/
│   └── main.py         ← MicroPython for RP2040
└── README.md           ← This file
```

---

*VSeq — Built for hardware engineers who want a real-time, multi-channel voltage view without a RM3000 scope.*
