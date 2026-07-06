/*
  VSeq Firmware — STM32 (stm32.ino)
  Written for Arduino IDE with STM32 Cores (STM32duino)
  Compatible with STM32F103C8T6 (Blue Pill), STM32F401, STM32F411, etc.
  
  Reads 10 internal ADC channels directly and streams voltage data over USB CDC Serial.
  This avoids the need for external SPI ADC chips (MCP3204/8) since STM32 has 10+ ADC pins.
  
  Default Pin mapping on STM32F103C8T6 (Blue Pill):
    - CH0: PA0 (A0) - VCC_12V (Requires Voltage Divider)
    - CH1: PA1 (A1) - VCC_5V  (Requires Voltage Divider)
    - CH2: PA2 (A2) - VCC_3V3 (Direct / Divider)
    - CH3: PA3 (A3) - TRIGGER (Direct / Divider)
    - CH4: PA4 (A4) - VRM_CORE
    - CH5: PA5 (A5) - VRAM
    - CH6: PA6 (A6) - V_FAN   (Requires Voltage Divider)
    - CH7: PA7 (A7) - VDDCI
    - CH8: PB0 (A8) - PGOOD
    - CH9: PB1 (A9) - VSOC
    
  ⚠️ WARNING: All input voltages exceeding 3.3V MUST use voltage dividers.
*/

#include <Arduino.h>

#define BAUD_RATE 921600
#define ADC_RESOLUTION 12 // 12-bit ADC (0 - 4095)
#define VREF 3.3f

// Pin mapping for 10 ADC channels
const int ADC_PINS[10] = {
  PA0, // CH0 - A0 (VCC_12V via divider)
  PA1, // CH1 - A1 (VCC_5V via divider)
  PA2, // CH2 - A2 (VCC_3V3 direct)
  PA3, // CH3 - A3 (TRIGGER direct)
  PA4, // CH4 - A4 (VRM_CORE direct)
  PA5, // CH5 - A5 (VRAM direct)
  PA6, // CH6 - A6 (V_FAN via divider)
  PA7, // CH7 - A7 (VDDCI direct)
  PB0, // CH8 - A8 (PGOOD direct)
  PB1  // CH9 - A9 (VSOC direct)
};

// Voltage mapping coefficients for y = m * x + c (to map -30V..+30V input to 0..3.3V ADC pin)
// With E12 resistors: R1 (Input) = 100k, R2 (Bias to 3.3V) = 10k, R3 (to GND) = 12k
// Vin = Vx * (1 + R1/R2 + R1/R3) - V_BIAS * (R1/R2)
// Vin = Vx * 19.3333f - 33.0f
const float CAL_M[10] = {19.3333f, 19.3333f, 19.3333f, 19.3333f, 19.3333f, 19.3333f, 19.3333f, 19.3333f, 19.3333f, 19.3333f};
const float CAL_C[10] = {-33.0000f, -33.0000f, -33.0000f, -33.0000f, -33.0000f, -33.0000f, -33.0000f, -33.0000f, -33.0000f, -33.0000f};

bool running = false;
unsigned long sampleIntervalUs = 1000; // default 1000us (1kHz)
unsigned long nextSampleUs = 0;
unsigned long t0_ms = 0;

void handleCommand(String cmd) {
  cmd.trim();
  if (cmd == "START") {
    running = true;
    t0_ms = millis();
    nextSampleUs = micros();
  } else if (cmd == "STOP") {
    running = false;
  } else if (cmd.startsWith("RATE:")) {
    long hz = cmd.substring(5).toInt();
    if (hz > 0) {
      sampleIntervalUs = 1000000 / min(5000L, max(1L, hz));
    }
  } else if (cmd == "ID?") {
    Serial.println("# VSeq v1.0 STM32 10ch");
  }
}

void setup() {
  // Initialize USB Serial (CDC)
  Serial.begin(BAUD_RATE);
  
  // Set ADC resolution (12-bit is native for STM32)
  analogReadResolution(ADC_RESOLUTION);
  
  // Configure analog pins as analog inputs
  for (int i = 0; i < 10; i++) {
    pinMode(ADC_PINS[i], INPUT_ANALOG);
  }
}

void loop() {
  // Read incoming serial commands
  if (Serial.available() > 0) {
    String cmd = Serial.readStringUntil('\n');
    handleCommand(cmd);
  }

  if (!running) {
    delay(10);
    return;
  }

  // Rate-limited sampling
  unsigned long now = micros();
  if (now >= nextSampleUs) {
    nextSampleUs += sampleIntervalUs;
    
    float t_ms = (float)(millis() - t0_ms);
    
    // Print timestamp
    Serial.print(t_ms, 3);
    
    // Read and print each channel
    for (int i = 0; i < 10; i++) {
      int raw = analogRead(ADC_PINS[i]);
      float vx = ((float)raw / 4095.0f) * VREF;
      float voltage = vx * CAL_M[i] + CAL_C[i];
      Serial.print(",");
      Serial.print(voltage, 4);
    }
    Serial.println();
  }
}
