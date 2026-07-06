import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A3, landscape
from reportlab.lib import colors

def draw_resistor_symbol(c, x, y, horizontal=True, label="R", val="1M"):
    c.setStrokeColor(colors.HexColor("#00ff88"))
    c.setLineWidth(1.2)
    c.setFillColor(colors.HexColor("#0c1118"))
    
    if horizontal:
        # Lead in
        c.line(x, y, x + 10, y)
        # Resistor body box (20x8)
        c.rect(x + 10, y - 4, 20, 8, fill=1, stroke=1)
        # Lead out
        c.line(x + 30, y, x + 40, y)
        # Labels
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.setFont("Helvetica-Bold", 7)
        c.drawCentredString(x + 20, y + 6, label)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + 20, y - 10, val)
    else:
        # Lead in
        c.line(x, y, x, y - 10)
        # Resistor body box (8x20)
        c.rect(x - 4, y - 30, 8, 20, fill=1, stroke=1)
        # Lead out
        c.line(x, y - 30, x, y - 40)
        # Labels
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.setFont("Helvetica-Bold", 7)
        c.drawString(x + 6, y - 16, label)
        c.setFont("Helvetica", 6)
        c.drawString(x + 6, y - 26, val)

def draw_zener_symbol(c, x, y, label="D", val="3.3V"):
    c.setStrokeColor(colors.HexColor("#ff5555"))
    c.setLineWidth(1.2)
    c.setFillColor(colors.HexColor("#0c1118"))
    
    # Lead in from top
    c.line(x, y, x, y - 10)
    # Zener Triangle pointing down (12x10)
    p = c.beginPath()
    p.moveTo(x - 6, y - 10)
    p.lineTo(x + 6, y - 10)
    p.lineTo(x, y - 20)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Cathode bar with Z-wings
    c.line(x - 6, y - 20, x + 6, y - 20)
    c.line(x - 6, y - 20, x - 6, y - 18)
    c.line(x + 6, y - 22, x + 6, y - 20)
    # Lead out to GND
    c.line(x, y - 20, x, y - 30)
    # Labels
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.setFont("Helvetica-Bold", 7)
    c.drawString(x + 8, y - 12, label)
    c.setFont("Helvetica", 6)
    c.drawString(x + 8, y - 22, val)

def draw_opamp_symbol(c, x, y, label="U", unit="A"):
    c.setStrokeColor(colors.HexColor("#c77dff"))
    c.setLineWidth(1.2)
    c.setFillColor(colors.HexColor("#0c1118"))
    
    # Triangle body
    p = c.beginPath()
    p.moveTo(x, y - 15)
    p.lineTo(x, y + 15)
    p.lineTo(x + 25, y)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    
    # Inputs + and -
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.drawString(x + 2, y + 5, "+")
    c.drawString(x + 2, y - 9, "-")
    
    # Input lines
    c.setStrokeColor(colors.HexColor("#c77dff"))
    c.line(x - 10, y + 7, x, y + 7) # Non-inverting input (+)
    c.line(x - 10, y - 7, x, y - 7) # Inverting input (-)
    
    # Output line
    c.line(x + 25, y, x + 35, y) # Output
    
    # Labels
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.HexColor("#c77dff"))
    c.drawCentredString(x + 12, y - 3, f"{label}{unit}")

def draw_gnd_symbol(c, x, y):
    c.setStrokeColor(colors.HexColor("#6e8099"))
    c.setLineWidth(1.2)
    c.line(x, y, x, y - 5)
    c.line(x - 6, y - 5, x + 6, y - 5)
    c.line(x - 4, y - 7, x + 4, y - 7)
    c.line(x - 2, y - 9, x + 2, y - 9)

def draw_vcc_arrow(c, x, y):
    c.setStrokeColor(colors.HexColor("#ff6b6b"))
    c.setLineWidth(1.2)
    c.line(x, y, x, y + 5)
    # Triangle pointing up
    p = c.beginPath()
    p.moveTo(x - 4, y + 5)
    p.lineTo(x + 4, y + 5)
    p.lineTo(x, y + 10)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#ff6b6b"))
    c.setFont("Helvetica-Bold", 6)
    c.drawString(x + 6, y + 6, "+3.3V")

def generate_pdf():
    pdf_path = "/Users/noorzoolhilmi/Desktop/vseq/schematic.pdf"
    # Use A3 landscape (1190.55 x 841.89 points) to fit all 10 channels cleanly side-by-side
    pagesize = landscape(A3)
    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    width, height = pagesize # 1190.55 x 841.89

    # Dark Background
    c.setFillColor(colors.HexColor("#060a0e"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Frame Borders
    c.setStrokeColor(colors.HexColor("#101820"))
    c.setLineWidth(4)
    c.rect(15, 15, width - 30, height - 30)
    c.setStrokeColor(colors.HexColor("#1a2535"))
    c.setLineWidth(1)
    c.rect(20, 20, width - 40, height - 40)

    # Schematic Grid (subtle)
    c.setStrokeColor(colors.HexColor("#0c1118"))
    c.setLineWidth(0.5)
    for x in range(40, int(width) - 20, 20):
        c.line(x, 20, x, height - 20)
    for y in range(40, int(height) - 20, 20):
        c.line(20, y, width - 20, y)

    # Title Block Block
    c.setFillColor(colors.HexColor("#0c1118"))
    c.setStrokeColor(colors.HexColor("#1a2535"))
    c.rect(20, height - 70, width - 40, 50, fill=1, stroke=1)
    
    c.setFillColor(colors.HexColor("#00ff88"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 52, "VSeq — FULL 10-CHANNEL HARDWARE SCHEMATIC (STM32 VERSION)")
    
    c.setFillColor(colors.HexColor("#6e8099"))
    c.setFont("Helvetica", 9)
    c.drawString(40, height - 64, "Input Range: -30V to +30V (Every Channel)  |  Input Impedance: 1M Ohm  |  Op-Amp Active Overvoltage Protection Clamp")

    # 10 Channels Configuration
    ch_names = ["VCC_12V", "VCC_5V", "VCC_3V3", "TRIGGER", "VRM_CORE", "VRAM", "V_FAN", "VDDCI", "PGOOD", "VSOC"]
    stm32_pins = ["PA0 (ADC0)", "PA1 (ADC1)", "PA2 (ADC2)", "PA3 (ADC3)", "PA4 (ADC4)", "PA5 (ADC5)", "PA6 (ADC6)", "PA7 (ADC7)", "PB0 (ADC8)", "PB1 (ADC9)"]

    # 1. STM32 Board Block (Right Side)
    mcu_x = 880
    mcu_y = 60
    mcu_w = 260
    mcu_h = 680
    c.setFillColor(colors.HexColor("#0c1118"))
    c.setStrokeColor(colors.HexColor("#4db8ff"))
    c.setLineWidth(2)
    c.rect(mcu_x, mcu_y, mcu_w, mcu_h, fill=1, stroke=1)

    c.setFillColor(colors.HexColor("#4db8ff"))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(mcu_x + mcu_w/2, mcu_y + mcu_h - 25, "STM32F103C8T6 BLUE PILL")
    c.setFillColor(colors.HexColor("#6e8099"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(mcu_x + mcu_w/2, mcu_y + mcu_h - 38, "(12-BIT NATIVE ADC CHANNELS)")

    # 2. Draw 10 Channels
    start_y = 700
    spacing_y = 64
    
    for i in range(10):
        y = start_y - (i * spacing_y)
        
        # Channel alias label
        c.setFillColor(colors.HexColor("#ffd23f"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(30, y + 10, f"CH{i} — {ch_names[i]}")
        c.setFillColor(colors.HexColor("#6e8099"))
        c.setFont("Helvetica-Bold", 6)
        c.drawString(30, y - 2, "PROBE TIP")
        
        # Probe circle node
        c.setStrokeColor(colors.HexColor("#ffd23f"))
        c.setLineWidth(1.5)
        c.circle(100, y, 3, fill=0, stroke=1)
        c.line(103, y, 120, y) # lead in line
        
        # R1 (Input Resistor 1M)
        draw_resistor_symbol(c, 120, y, horizontal=True, label=f"R{i*3+1}", val="1M")
        
        # Vx Node
        vx_x = 180
        c.setStrokeColor(colors.HexColor("#00ff88"))
        c.line(160, y, 220, y) # connection line
        c.setFillColor(colors.HexColor("#00ff88"))
        c.circle(vx_x, y, 2, fill=1, stroke=0) # Junction Vx
        
        # R2 (Bias Resistor 100k UP to +3.3V)
        draw_resistor_symbol(c, vx_x, y + 40, horizontal=False, label=f"R{i*3+2}", val="100k")
        c.setStrokeColor(colors.HexColor("#00ff88"))
        c.line(vx_x, y, vx_x, y + 10)
        draw_vcc_arrow(c, vx_x, y + 40)
        
        # R3 (Gnd Resistor 120k DOWN to GND)
        draw_resistor_symbol(c, vx_x, y, horizontal=False, label=f"R{i*3+3}", val="120k")
        draw_gnd_symbol(c, vx_x, y - 40)
        
        # Zener Diode (3.3V Clamp to GND)
        z_x = 220
        c.setStrokeColor(colors.HexColor("#00ff88"))
        c.line(vx_x, y, 250, y) # extension line
        c.circle(z_x, y, 2, fill=1, stroke=0) # Junction Zener
        draw_zener_symbol(c, z_x, y, label=f"D{i+1}", val="3.3V")
        draw_gnd_symbol(c, z_x, y - 30)
        
        # Op-Amp Buffer Unit (MCP6002)
        op_x = 265
        op_ref = f"U{i//2+1}"
        op_unit = chr(65 + (i % 2)) # A or B
        draw_opamp_symbol(c, op_x, y, label=op_ref, unit=op_unit)
        # Wire to non-inverting input (+)
        c.setStrokeColor(colors.HexColor("#00ff88"))
        c.line(250, y, op_x - 10, y + 7)
        
        # Op-Amp Feedback loop (Inverting input (-) to output)
        # Feedback loop: (-) input is at op_x-10, y-7. Output is at op_x+35, y.
        c.setStrokeColor(colors.HexColor("#c77dff"))
        c.line(op_x - 10, y - 7, op_x - 15, y - 7)
        c.line(op_x - 15, y - 7, op_x - 15, y - 22)
        c.line(op_x - 15, y - 22, op_x + 40, y - 22)
        c.line(op_x + 40, y - 22, op_x + 40, y)
        c.line(op_x + 35, y, op_x + 40, y)
        c.circle(op_x + 40, y, 2, fill=1, stroke=0) # Junction Output
        
        # Output net label wire all the way to MCU
        c.setStrokeColor(colors.HexColor("#00ff88"))
        c.line(op_x + 40, y, mcu_x, y)
        
        # PCB Net Name
        c.setFillColor(colors.HexColor("#00ff88"))
        c.setFont("Helvetica-Bold", 7)
        c.drawString(op_x + 50, y + 5, f"CH{i}_ADC")
        
        # MCU Pin label & marker on the board
        c.setFillColor(colors.HexColor("#4db8ff"))
        c.circle(mcu_x, y, 3, fill=1, stroke=0)
        c.setFont("Helvetica-Bold", 8)
        c.drawString(mcu_x + 10, y - 3, stm32_pins[i])
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.setFont("Helvetica", 7)
        c.drawString(mcu_x + 105, y - 3, f"← CH{i}_ADC Net")

    # Legend Box (Bottom Right)
    leg_x = mcu_x
    leg_y = mcu_y
    c.setFillColor(colors.HexColor("#0c1118"))
    c.setStrokeColor(colors.HexColor("#101820"))
    c.rect(leg_x, leg_y, mcu_w, 100, fill=1, stroke=1)
    
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(leg_x + 15, leg_y + 80, "DOCUMENT INFORMATION")
    c.setFont("Helvetica", 8)
    c.setFillColor(colors.HexColor("#6e8099"))
    c.drawString(leg_x + 15, leg_y + 60, "Project: VSeq Bipolar Voltage Analyzer")
    c.drawString(leg_x + 15, leg_y + 45, "Schematic Version: Rev 1.2 (Full 10-Channel)")
    c.drawString(leg_x + 15, leg_y + 30, "Date: 2026-07-06  |  Author: Antigravity")

    # Save
    c.showPage()
    c.save()
    print("Successfully generated full schematic.pdf")

if __name__ == "__main__":
    generate_pdf()
