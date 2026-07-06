import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors

def draw_resistor(c, x, y, horizontal=True, label="R"):
    c.setStrokeColor(colors.HexColor("#00ff88"))
    c.setLineWidth(1.5)
    if horizontal:
        # Lead in
        c.line(x, y, x + 15, y)
        # Resistor body box
        c.rect(x + 15, y - 6, 25, 12, fill=1, stroke=1)
        # Lead out
        c.line(x + 40, y, x + 55, y)
        # Label
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.setFont("Helvetica-Bold", 8)
        c.drawCentredString(x + 27.5, y + 10, label)
    else:
        # Lead in
        c.line(x, y, x, y - 15)
        # Resistor body box
        c.rect(x - 6, y - 40, 12, 25, fill=1, stroke=1)
        # Lead out
        c.line(x, y - 40, x, y - 55)
        # Label
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.setFont("Helvetica-Bold", 8)
        c.drawString(x + 10, y - 27.5, label)

def draw_zener(c, x, y, label="3.3V"):
    c.setStrokeColor(colors.HexColor("#ff5555"))
    c.setLineWidth(1.5)
    # Lead in (from top)
    c.line(x, y, x, y - 15)
    # Triangle (pointing down)
    p = c.beginPath()
    p.moveTo(x - 8, y - 15)
    p.lineTo(x + 8, y - 15)
    p.lineTo(x, y - 30)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    # Cathode bar with Z-wings
    c.line(x - 8, y - 30, x + 8, y - 30)
    c.line(x - 8, y - 30, x - 8, y - 27)
    c.line(x + 8, y - 33, x + 8, y - 30)
    # Lead out to GND
    c.line(x, y - 30, x, y - 45)
    # Label
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(x + 12, y - 25, label)

def draw_gnd(c, x, y):
    c.setStrokeColor(colors.HexColor("#6e8099"))
    c.setLineWidth(1.5)
    c.line(x, y, x, y - 8)
    c.line(x - 10, y - 8, x + 10, y - 8)
    c.line(x - 6, y - 11, x + 6, y - 11)
    c.line(x - 2, y - 14, x + 2, y - 14)

def draw_opamp(c, x, y, label="MCP6002"):
    c.setStrokeColor(colors.HexColor("#4db8ff"))
    c.setLineWidth(1.5)
    c.setFillColor(colors.HexColor("#0c1118"))
    p = c.beginPath()
    p.moveTo(x, y - 25)
    p.lineTo(x, y + 25)
    p.lineTo(x + 40, y)
    p.close()
    c.drawPath(p, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 8)
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.drawString(x + 3, y + 10, "+")
    c.drawString(x + 3, y - 14, "-")
    c.setStrokeColor(colors.HexColor("#4db8ff"))
    c.line(x - 15, y + 12, x, y + 12)
    c.line(x - 15, y - 12, x, y - 12)
    c.line(x + 40, y, x + 55, y)
    c.line(x - 15, y - 12, x - 15, y - 30)
    c.line(x - 15, y - 30, x + 48, y - 30)
    c.line(x + 48, y - 30, x + 48, y)
    c.setFont("Helvetica-Bold", 7)
    c.setFillColor(colors.HexColor("#4db8ff"))
    c.drawCentredString(x + 18, y - 4, label)

def generate_pdf():
    pdf_path = "/Users/noorzoolhilmi/Desktop/vseq/schematic.pdf"
    pagesize = landscape(A4)
    c = canvas.Canvas(pdf_path, pagesize=pagesize)
    width, height = pagesize # 841.89 x 595.27

    # 1. Dark Background Theme
    c.setFillColor(colors.HexColor("#060a0e"))
    c.rect(0, 0, width, height, fill=1, stroke=0)

    # Outer Border Frame
    c.setStrokeColor(colors.HexColor("#101820"))
    c.setLineWidth(4)
    c.rect(15, 15, width - 30, height - 30)
    c.setStrokeColor(colors.HexColor("#1a2535"))
    c.setLineWidth(1)
    c.rect(20, 20, width - 40, height - 40)

    # Grid Pattern (Subtle)
    c.setStrokeColor(colors.HexColor("#0c1118"))
    c.setLineWidth(0.5)
    for x in range(40, int(width) - 20, 20):
        c.line(x, 20, x, height - 20)
    for y in range(40, int(height) - 20, 20):
        c.line(20, y, width - 20, y)

    # Title Block Header
    c.setFillColor(colors.HexColor("#0c1118"))
    c.rect(20, height - 70, width - 40, 50, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#00ff88"))
    c.setFont("Helvetica-Bold", 18)
    c.drawString(40, height - 52, "VSeq — 10-CHANNEL VOLTAGE SEQUENCER SCHEMATIC")
    c.setFillColor(colors.HexColor("#6e8099"))
    c.setFont("Helvetica", 9)
    c.drawString(40, height - 64, "Platform: STM32F103C8T6 (Blue Pill)  |  Bipolar Input Range: -30V to +30V Level Shifter (E12 Resistors)")

    # 2. STM32 Blue Pill Board Block (Right Side)
    mcu_x, mcu_y = 520, 90
    mcu_w, mcu_h = 240, 360
    c.setFillColor(colors.HexColor("#0c1118"))
    c.setStrokeColor(colors.HexColor("#4db8ff"))
    c.setLineWidth(2)
    c.rect(mcu_x, mcu_y, mcu_w, mcu_h, fill=1, stroke=1)

    # MCU Header Label
    c.setFillColor(colors.HexColor("#4db8ff"))
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(mcu_x + mcu_w/2, mcu_y + mcu_h - 22, "STM32F103C8T6 BOARD")
    c.setFillColor(colors.HexColor("#6e8099"))
    c.setFont("Helvetica", 8)
    c.drawCentredString(mcu_x + mcu_w/2, mcu_y + mcu_h - 34, "(BLUE PILL / BLACK PILL)")

    # Pin Markers inside MCU block
    pins = [
        ("PA0 (ADC0)", "CH0 - VCC_12V (±30V)"),
        ("PA1 (ADC1)", "CH1 - VCC_5V (±30V)"),
        ("PA2 (ADC2)", "CH2 - VCC_3V3 (±30V)"),
        ("PA3 (ADC3)", "CH3 - TRIGGER (±30V)"),
        ("PA4 (ADC4)", "CH4 - VRM_CORE (±30V)"),
        ("PA5 (ADC5)", "CH5 - VRAM (±30V)"),
        ("PA6 (ADC6)", "CH6 - V_FAN (±30V)"),
        ("PA7 (ADC7)", "CH7 - VDDCI (±30V)"),
        ("PB0 (ADC8)", "CH8 - PGOOD (±30V)"),
        ("PB1 (ADC9)", "CH9 - VSOC (±30V)")
    ]

    c.setFont("Helvetica-Bold", 9)
    for idx, (pin, label) in enumerate(pins):
        py = mcu_y + mcu_h - 70 - (idx * 28)
        # Pin dot
        c.setFillColor(colors.HexColor("#4db8ff"))
        c.circle(mcu_x, py, 3, fill=1, stroke=0)
        # Text labels
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.drawString(mcu_x + 10, py - 3, pin)
        c.setFillColor(colors.HexColor("#6e8099"))
        c.drawString(mcu_x + 95, py - 3, f"← {label}")

    # USB Connector Box
    usb_x, usb_y = mcu_x + 70, mcu_y - 25
    c.setFillColor(colors.HexColor("#101820"))
    c.setStrokeColor(colors.HexColor("#6e8099"))
    c.rect(usb_x, usb_y, 100, 25, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.setFont("Helvetica-Bold", 8)
    c.drawCentredString(usb_x + 50, usb_y + 9, "USB Type-C / Micro")
    # Connection line to PC
    c.setStrokeColor(colors.HexColor("#6e8099"))
    c.line(usb_x + 50, usb_y, usb_x + 50, usb_y - 15)
    c.drawCentredString(usb_x + 50, usb_y - 25, "TO PC (USB CDC)")

    # 3. Typical Input Channel Stage Drawing (Left Side)
    stage_x = 60
    c.setFillColor(colors.HexColor("#e0eaf5"))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(stage_x, 460, "BIPOLAR LEVEL SHIFTER (-30V TO +30V INPUT)")

    # Probe Tip
    probe_y = 390
    c.setStrokeColor(colors.HexColor("#ffd23f"))
    c.setLineWidth(2)
    c.line(stage_x, probe_y, stage_x + 40, probe_y)
    c.setFillColor(colors.HexColor("#ffd23f"))
    c.circle(stage_x, probe_y, 4, fill=1, stroke=1)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(stage_x - 10, probe_y + 10, "PROBE TIP (-30V..+30V)")

    # R1 Resistor
    draw_resistor(c, stage_x + 40, probe_y, horizontal=True, label="R1 (Input) 1M")

    # Node Vx
    vx_x = stage_x + 95
    c.line(vx_x, probe_y, vx_x + 120, probe_y) # Line to Op-Amp (+)
    c.setFillColor(colors.HexColor("#00ff88"))
    c.circle(vx_x + 30, probe_y, 3, fill=1, stroke=0)
    c.circle(vx_x + 70, probe_y, 3, fill=1, stroke=0)

    # R2 Resistor pointing UP to 3.3V Bias
    r2_node = vx_x + 30
    draw_resistor(c, r2_node, probe_y + 55, horizontal=False, label="R2 (Bias) 100k")
    c.setStrokeColor(colors.HexColor("#ff5555"))
    c.line(r2_node - 8, probe_y + 55, r2_node + 8, probe_y + 55)
    c.setFillColor(colors.HexColor("#ff5555"))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(r2_node + 12, probe_y + 52, "+3.3V VREF")

    # R3 Resistor pointing DOWN to GND
    draw_resistor(c, r2_node, probe_y, horizontal=False, label="R3 (GND) 120k")
    draw_gnd(c, r2_node, probe_y - 55)

    # Zener Protection clamp
    z_node = vx_x + 70
    draw_zener(c, z_node, probe_y, label="Zener 3.3V Clamp")
    draw_gnd(c, z_node, probe_y - 45)

    # Draw Op-Amp Buffer
    op_x = vx_x + 120
    draw_opamp(c, op_x, probe_y - 12, label="MCP6002")

    # Output line from Op-Amp to ADC pin marker
    c.setStrokeColor(colors.HexColor("#4db8ff"))
    c.line(op_x + 55, probe_y - 12, op_x + 75, probe_y - 12)

    # Output to STM32 Node
    out_x = op_x + 75
    c.setFillColor(colors.HexColor("#4db8ff"))
    c.circle(out_x, probe_y - 12, 4, fill=1, stroke=0)
    c.setFont("Helvetica-Bold", 10)
    c.drawString(out_x - 10, probe_y + 2, "TO ADC PIN (PA0-PA7, PB0-PB1)")

    # 4. Connection Mapping Table (Bottom Left)
    tbl_x, tbl_y = 60, 90
    c.setFillColor(colors.HexColor("#101820"))
    c.setStrokeColor(colors.HexColor("#1a2535"))
    c.rect(tbl_x, tbl_y, 400, 240, fill=1, stroke=1)

    # Table Header
    c.setFillColor(colors.HexColor("#1a2535"))
    c.rect(tbl_x, tbl_y + 215, 400, 25, fill=1, stroke=0)
    c.setFillColor(colors.HexColor("#00ff88"))
    c.setFont("Helvetica-Bold", 9)
    c.drawString(tbl_x + 10, tbl_y + 225, "VSeq CH")
    c.drawString(tbl_x + 70, tbl_y + 225, "Pin")
    c.drawString(tbl_x + 130, tbl_y + 225, "Signal / Rail")
    c.drawString(tbl_x + 220, tbl_y + 225, "R1 (Input)")
    c.drawString(tbl_x + 290, tbl_y + 225, "R2 (Bias)")
    c.drawString(tbl_x + 350, tbl_y + 225, "R3 (Gnd)")

    # Table Rows
    table_data = [
        ("CH0", "PA0", "VCC_12V", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH1", "PA1", "VCC_5V", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH2", "PA2", "VCC_3V3", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH3", "PA3", "TRIGGER", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH4", "PA4", "VRM_CORE", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH5", "PA5", "VRAM", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH6", "PA6", "V_FAN", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH7", "PA7", "VDDCI", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH8", "PB0", "PGOOD", "1 MOhm", "100 kOhm", "120 kOhm"),
        ("CH9", "PB1", "VSOC", "1 MOhm", "100 kOhm", "120 kOhm")
    ]

    c.setFont("Helvetica", 8)
    for idx, row in enumerate(table_data):
        ry = tbl_y + 195 - (idx * 20)
        # Alternate row background
        if idx % 2 == 1:
            c.setFillColor(colors.HexColor("#0c1118"))
            c.rect(tbl_x + 2, ry - 4, 396, 18, fill=1, stroke=0)
            
        c.setFillColor(colors.HexColor("#e0eaf5"))
        c.drawString(tbl_x + 10, ry, row[0])
        c.drawString(tbl_x + 70, ry, row[1])
        c.drawString(tbl_x + 130, ry, row[2])
        c.drawString(tbl_x + 220, ry, row[3])
        c.drawString(tbl_x + 290, ry, row[4])
        c.setFillColor(colors.HexColor("#ffd23f") if "Direct" not in row[3] else colors.HexColor("#00ff88"))
        c.drawString(tbl_x + 350, ry, row[5])

    # Footer/Legend Box (Bottom Right Title Area)
    c.setFillColor(colors.HexColor("#0c1118"))
    c.setStrokeColor(colors.HexColor("#101820"))
    c.rect(width - 240, 20, 220, 50, fill=1, stroke=1)
    c.setFillColor(colors.HexColor("#6e8099"))
    c.setFont("Helvetica", 8)
    c.drawString(width - 230, 52, "Doc: VSeq Hardware Schematic")
    c.drawString(width - 230, 40, "Revision: v1.1 (STM32 ADC Only)")
    c.drawString(width - 230, 28, "Date: 2026-07-06  |  Author: Antigravity")

    # Complete page
    c.showPage()
    c.save()
    print("Successfully generated schematic.pdf at", pdf_path)

if __name__ == "__main__":
    generate_pdf()
