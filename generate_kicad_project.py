import os
import uuid

def generate_uuid():
    return str(uuid.uuid4())

def create_kicad_project():
    project_dir = "/Users/noorzoolhilmi/Desktop/vseq/kicad_project"
    os.makedirs(project_dir, exist_ok=True)

    # 1. Project file (vseq.kicad_pro)
    pro_path = os.path.join(project_dir, "vseq.kicad_pro")
    pro_content = """{
  "meta": {
    "version": 1
  },
  "project": {
    "back_annotated_footprints": [],
    "back_annotated_net_names": [],
    "back_annotated_pads": []
  }
}"""
    with open(pro_path, "w") as f:
        f.write(pro_content)

    # 2. Schematic file (vseq.kicad_sch)
    sch_path = os.path.join(project_dir, "vseq.kicad_sch")
    
    # We will build the S-expression string
    sexp = []
    sexp.append('(kicad_sch (version 20230121) (generator eeschema)')
    sexp.append(f'  (uuid "{generate_uuid()}")')
    sexp.append('  (paper "A3")')
    sexp.append('  (title_block')
    sexp.append('    (title "VSeq 10-Channel Bipolar Voltage Analyzer")')
    sexp.append('    (company "Antigravity")')
    sexp.append('    (rev "1.2")')
    sexp.append('    (date "2026-07-06")')
    sexp.append('  )')
    
    # Symbol Library Definitions
    sexp.append('  (lib_symbols')
    
    # Device:R definition
    sexp.append('    (symbol "Device:R" (in_bom yes) (on_board yes)')
    sexp.append('      (property "Reference" "R" (id 0) (at 2.032 0 90) (effects (font (size 1.27 1.27))))')
    sexp.append('      (property "Value" "R" (id 1) (at 2.032 -2.54 90) (effects (font (size 1.27 1.27))))')
    sexp.append('      (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (symbol "R_0_1"')
    sexp.append('        (rectangle (start -1.016 -3.81) (end 1.016 3.81) (stroke (width 0.254)) (fill (type outline)))')
    sexp.append('      )')
    sexp.append('      (symbol "R_1_1"')
    sexp.append('        (pin passive line (at 0 5.08 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sexp.append('        (pin passive line (at 0 -5.08 90) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sexp.append('      )')
    sexp.append('    )')
    
    # Device:D_Zener definition
    sexp.append('    (symbol "Device:D_Zener" (in_bom yes) (on_board yes)')
    sexp.append('      (property "Reference" "D" (id 0) (at -1.27 2.54 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sexp.append('      (property "Value" "D_Zener" (id 1) (at -1.27 -2.54 0) (effects (font (size 1.27 1.27)) (justify left)))')
    sexp.append('      (property "Footprint" "Diode_SMD:D_SOD-123" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (symbol "D_Zener_0_1"')
    sexp.append('        (polyline (pts (xy 0 -1.27) (xy 0 1.27)) (stroke (width 0.254)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy 0 -1.27) (xy -0.635 -1.524)) (stroke (width 0.254)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy 0 1.27) (xy 0.635 1.524)) (stroke (width 0.254)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy -1.27 1.27) (xy 1.27 0) (xy -1.27 -1.27) (xy -1.27 1.27)) (stroke (width 0.254)) (fill (type outline)))')
    sexp.append('      )')
    sexp.append('      (symbol "D_Zener_1_1"')
    sexp.append('        (pin passive line (at -3.81 0 0) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sexp.append('        (pin passive line (at 3.81 0 180) (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sexp.append('      )')
    sexp.append('    )')
    
    # MCP6002 definition (Op-Amp)
    sexp.append('    (symbol "Amplifier_Operational:MCP6002" (in_bom yes) (on_board yes)')
    sexp.append('      (property "Reference" "U" (id 0) (at -15.24 7.62 0) (effects (font (size 1.27 1.27))))')
    sexp.append('      (property "Value" "MCP6002" (id 1) (at -15.24 5.08 0) (effects (font (size 1.27 1.27))))')
    sexp.append('      (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (symbol "MCP6002_0_1"')
    sexp.append('        (polyline (pts (xy -5.08 5.08) (xy -5.08 -5.08) (xy 5.08 0) (xy -5.08 5.08)) (stroke (width 0.254)) (fill (type outline)))')
    sexp.append('      )')
    sexp.append('      (symbol "MCP6002_1_1"')
    sexp.append('        (pin input line (at -10.16 2.54 0) (length 5.08) (name "+" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sexp.append('        (pin input line (at -10.16 -2.54 0) (length 5.08) (name "-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    sexp.append('        (pin output line (at 10.16 0 180) (length 5.08) (name "~" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    sexp.append('      )')
    sexp.append('    )')

    # Connector block (Probe input 10-pin connector)
    sexp.append('    (symbol "Connector:Conn_01x10_Male" (in_bom yes) (on_board yes)')
    sexp.append('      (property "Reference" "J" (id 0) (at 0 12.7 0) (effects (font (size 1.27 1.27))))')
    sexp.append('      (property "Value" "Conn_01x10_Male" (id 1) (at 0 10.16 0) (effects (font (size 1.27 1.27))))')
    sexp.append('      (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical" (id 2) (at 0 0 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (symbol "Conn_01x10_Male_1_1"')
    for p in range(1, 11):
        py = 12.7 - p * 2.54
        sexp.append(f'        (pin passive line (at -5.08 {py:.2f} 0) (length 5.08) (name "Pin_{p}" (effects (font (size 1.27 1.27)))) (number "{p}" (effects (font (size 1.27 1.27)))))')
    sexp.append('      )')
    sexp.append('    )')

    # GND power port
    sexp.append('    (symbol "power:GND" (power) (in_bom no) (on_board yes)')
    sexp.append('      (property "Reference" "#PWR" (id 0) (at 0 -6.35 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (property "Value" "GND" (id 1) (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (symbol "GND_0_1"')
    sexp.append('        (polyline (pts (xy 0 0) (xy 0 -1.27)) (stroke (width 0.152)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy -2.54 -1.27) (xy 2.54 -1.27)) (stroke (width 0.152)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy -1.27 -2.54) (xy 1.27 -2.54)) (stroke (width 0.152)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy -0.635 -3.81) (xy 0.635 -3.81)) (stroke (width 0.152)) (fill (type none)))')
    sexp.append('      )')
    sexp.append('      (symbol "GND_1_1"')
    sexp.append('        (pin power_in line (at 0 0 270) (length 0) hide (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sexp.append('      )')
    sexp.append('    )')

    # +3.3V VREF power port
    sexp.append('    (symbol "power:+3.3V" (power) (in_bom no) (on_board yes)')
    sexp.append('      (property "Reference" "#PWR" (id 0) (at 0 -3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (property "Value" "+3.3V" (id 1) (at 0 3.81 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('      (symbol "+3.3V_0_1"')
    sexp.append('        (polyline (pts (xy 0 0) (xy 0 1.27)) (stroke (width 0.152)) (fill (type none)))')
    sexp.append('        (polyline (pts (xy 0 1.27) (xy -0.635 0.635) (xy 0 1.27) (xy 0.635 0.635)) (stroke (width 0.152)) (fill (type none)))')
    sexp.append('      )')
    sexp.append('      (symbol "+3.3V_1_1"')
    sexp.append('        (pin power_in line (at 0 0 90) (length 0) hide (name "+3.3V" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    sexp.append('      )')
    sexp.append('    )')

    sexp.append('  )') # End lib_symbols

    # Channels layout offset
    ch_names = ["VCC_12V", "VCC_5V", "VCC_3V3", "TRIGGER", "VRM_CORE", "VRAM", "V_FAN", "VDDCI", "PGOOD", "VSOC"]
    stm32_pins = ["PA0", "PA1", "PA2", "PA3", "PA4", "PA5", "PA6", "PA7", "PB0", "PB1"]

    # Draw 10 conditioning channels in vertical rows
    for i in range(10):
        # Y-coord of this channel row
        y = 50.8 + (i * 25.4)
        
        # 1. Probe input net text label & wire
        # Connector pin or net label on left
        sexp.append(f'  (label "PROBE_CH{i}" (at 40.64 {y:.2f} 180) (effects (font (size 1.27 1.27)) (justify right)))')
        sexp.append(f'  (wire (pts (xy 40.64 {y:.2f}) (xy 55.88 {y:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')

        # 2. Resistor R1 (1M) - Horizontal
        # Placement at x=60.96, y=y. Orientation 0 (horizontal)
        # Pins are at x=55.88 and x=66.04
        r1_ref = f"R{i*3 + 1}"
        sexp.append(f'  (symbol (lib_id "Device:R") (at 60.96 {y:.2f} 0) (unit 1)')
        sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "{r1_ref}" (id 0) (at 60.96 {y-3.81:.2f} 0))')
        sexp.append(f'    (property "Value" "1M" (id 1) (at 60.96 {y+3.81:.2f} 0))')
        sexp.append(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (id 2) (at 60.96 {y:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')

        # Wire from R1 out to Vx node
        vx_x = 76.2
        sexp.append(f'  (wire (pts (xy 66.04 {y:.2f}) (xy {vx_x:.2f} {y:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (junction (at {vx_x:.2f} {y:.2f}) (stroke (width 0)) (uuid "{generate_uuid()}"))')

        # 3. Resistor R2 (100k) - Vertical, going UP to +3.3V
        # Centered at x=76.2, y=y-12.7. Orientation 90 (vertical)
        # Pins are at y=y-17.78 (top) and y=y-7.62 (bottom)
        r2_ref = f"R{i*3 + 2}"
        sexp.append(f'  (symbol (lib_id "Device:R") (at {vx_x:.2f} {y-12.7:.2f} 90) (unit 1)')
        sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "{r2_ref}" (id 0) (at {vx_x+3.81:.2f} {y-12.7:.2f} 90))')
        sexp.append(f'    (property "Value" "100k" (id 1) (at {vx_x-3.81:.2f} {y-12.7:.2f} 90))')
        sexp.append(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (id 2) (at {vx_x:.2f} {y-12.7:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')
        # Wire from R2 Pin 2 to Vx
        sexp.append(f'  (wire (pts (xy {vx_x:.2f} {y-7.62:.2f}) (xy {vx_x:.2f} {y:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        # +3.3V power port on top of R2
        sexp.append(f'  (symbol (lib_id "power:+3.3V") (at {vx_x:.2f} {y-17.78:.2f} 0) (unit 1)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "#PWR" (id 0) (at {vx_x:.2f} {y-15.24:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append(f'    (property "Value" "+3.3V" (id 1) (at {vx_x:.2f} {y-20.32:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')

        # 4. Resistor R3 (120k) - Vertical, going DOWN to GND
        # Centered at x=76.2, y=y+12.7. Orientation 90 (vertical)
        # Pins are at y=y+7.62 (top) and y=y+17.78 (bottom)
        r3_ref = f"R{i*3 + 3}"
        sexp.append(f'  (symbol (lib_id "Device:R") (at {vx_x:.2f} {y+12.7:.2f} 90) (unit 1)')
        sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "{r3_ref}" (id 0) (at {vx_x+3.81:.2f} {y+12.7:.2f} 90))')
        sexp.append(f'    (property "Value" "120k" (id 1) (at {vx_x-3.81:.2f} {y+12.7:.2f} 90))')
        sexp.append(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (id 2) (at {vx_x:.2f} {y+12.7:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')
        # Wire Vx to R3 Pin 1
        sexp.append(f'  (wire (pts (xy {vx_x:.2f} {y:.2f}) (xy {vx_x:.2f} {y+7.62:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        # GND power port below R3
        sexp.append(f'  (symbol (lib_id "power:GND") (at {vx_x:.2f} {y+17.78:.2f} 0) (unit 1)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "#PWR" (id 0) (at {vx_x:.2f} {y+24.13:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append(f'    (property "Value" "GND" (id 1) (at {vx_x:.2f} {y+21.59:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')

        # 5. Zener Diode (Device:D_Zener) - Vertical, going DOWN to GND
        # Placed at x=88.90, y=y+12.7
        # In KiCad symbol, Pin 1 (Cathode) is at x=-3.81, Pin 2 (Anode) is at x=3.81 (horizontal orientation).
        # We rotate it 270 degrees so Cathode is pointing up (y=y+7.62) and Anode is pointing down (y=y+17.78).
        d_ref = f"D{i+1}"
        sexp.append(f'  (symbol (lib_id "Device:D_Zener") (at 88.90 {y+12.7:.2f} 270) (unit 1)')
        sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "{d_ref}" (id 0) (at 88.90 {y+7.62-2.54:.2f} 90))')
        sexp.append(f'    (property "Value" "3.3V" (id 1) (at 88.90 {y+17.78+2.54:.2f} 90))')
        sexp.append(f'    (property "Footprint" "Diode_SMD:D_SOD-123" (id 2) (at 88.90 {y+12.7:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')
        # Wire Vx to Zener Cathode
        sexp.append(f'  (wire (pts (xy {vx_x:.2f} {y:.2f}) (xy 88.90 {y:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (wire (pts (xy 88.90 {y:.2f}) (xy 88.90 {y+8.89:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (junction (at 88.90 {y:.2f}) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        # GND power port below Zener Anode
        sexp.append(f'  (symbol (lib_id "power:GND") (at 88.90 {y+17.78:.2f} 0) (unit 1)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "#PWR" (id 0) (at 88.90 {y+24.13:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append(f'    (property "Value" "GND" (id 1) (at 88.90 {y+21.59:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')

        # 6. Op-Amp Buffer Unit (MCP6002) - Placed at x=111.76, y=y
        # Non-inverting input (+) Pin 1 is at (x-10.16, y+2.54) => x=101.6, y=y-2.54 (in lib layout)
        # We rotate unit to standard, output is at x=121.92, y=y-2.54
        u_ref = f"U{i//2 + 1}"
        u_unit = (i % 2) + 1 # Unit A or B of the MCP6002 dual op-amp
        sexp.append(f'  (symbol (lib_id "Amplifier_Operational:MCP6002") (at 111.76 {y+2.54:.2f} 0) (unit {u_unit})')
        sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        sexp.append(f'    (uuid "{generate_uuid()}")')
        sexp.append(f'    (property "Reference" "{u_ref}" (id 0) (at 111.76 {y-7.62:.2f} 0))')
        sexp.append(f'    (property "Value" "MCP6002" (id 1) (at 111.76 {y-5.08:.2f} 0))')
        sexp.append(f'    (property "Footprint" "Package_SO:SOIC-8_3.9x4.9mm_P1.27mm" (id 2) (at 111.76 {y+2.54:.2f} 0) (effects (font (size 1.27 1.27)) hide))')
        sexp.append('  )')

        # Wire Node Vx to Op-Amp (+) Input (which is at x=101.60, y=y)
        sexp.append(f'  (wire (pts (xy 88.90 {y:.2f}) (xy 101.60 {y:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')

        # Feedback loop: Output pin (x=121.92, y=y+2.54) to Inverting input (-) Pin (x=101.6, y=y+5.08)
        # Draw wire from output: (121.92, y+2.54) -> (124.46, y+2.54) -> (124.46, y+7.62) -> (99.06, y+7.62) -> (99.06, y+5.08) -> (101.60, y+5.08)
        sexp.append(f'  (wire (pts (xy 121.92 {y+2.54:.2f}) (xy 124.46 {y+2.54:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (wire (pts (xy 124.46 {y+2.54:.2f}) (xy 124.46 {y+7.62:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (wire (pts (xy 124.46 {y+7.62:.2f}) (xy 99.06 {y+7.62:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (wire (pts (xy 99.06 {y+7.62:.2f}) (xy 99.06 {y+5.08:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (wire (pts (xy 99.06 {y+5.08:.2f}) (xy 101.60 {y+5.08:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')

        # Output label line and PCB Net label
        sexp.append(f'  (wire (pts (xy 124.46 {y+2.54:.2f}) (xy 134.62 {y+2.54:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (junction (at 124.46 {y+2.54:.2f}) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        # Place Net label cth: CH0_ADC
        sexp.append(f'  (label "CH{i}_ADC" (at 134.62 {y+2.54:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')

    # 7. Connector Header to represent the STM32 Analog Interface
    # Placed on the right side: x=215.9, y=114.3
    # Labeled as the STM32 ADC header, maps CH0_ADC..CH9_ADC to PA0..PA7, PB0, PB1
    sexp.append('  (symbol (lib_id "Connector:Conn_01x10_Male") (at 215.90 127.0 0) (unit 1)')
    sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
    sexp.append(f'    (uuid "{generate_uuid()}")')
    sexp.append('    (property "Reference" "J1" (id 0) (at 215.90 101.6 0))')
    sexp.append('    (property "Value" "STM32_ADC_IN" (id 1) (at 215.90 104.14 0))')
    sexp.append('    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical" (id 2) (at 215.90 127.0 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('  )')

    for i in range(10):
        py = 127.0 + 12.7 - (i+1) * 2.54
        # Connect each header pin of J1 to its respective CHx_ADC net label
        sexp.append(f'  (wire (pts (xy 210.82 {py:.2f}) (xy 195.58 {py:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (label "CH{i}_ADC" (at 195.58 {py:.2f} 180) (effects (font (size 1.27 1.27)) (justify right)))')
        # Pin description labels for PCB mapping
        sexp.append(f'  (label "{stm32_pins[i]}" (at 223.52 {py:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')

    # 8. Probe Header (J2) - Placed on the far left to act as a 10-pin interface for user probes
    sexp.append('  (symbol (lib_id "Connector:Conn_01x10_Male") (at 25.40 127.0 0) (unit 1)')
    sexp.append('    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
    sexp.append(f'    (uuid "{generate_uuid()}")')
    sexp.append('    (property "Reference" "J2" (id 0) (at 25.40 101.6 0))')
    sexp.append('    (property "Value" "PROBE_INPUTS" (id 1) (at 25.40 104.14 0))')
    sexp.append('    (property "Footprint" "Connector_PinHeader_2.54mm:PinHeader_1x10_P2.54mm_Vertical" (id 2) (at 25.40 127.0 0) (effects (font (size 1.27 1.27)) hide))')
    sexp.append('  )')

    for i in range(10):
        py = 127.0 + 12.7 - (i+1) * 2.54
        # Connect each pin of J2 to the PROBE_CHx net label
        sexp.append(f'  (wire (pts (xy 20.32 {py:.2f}) (xy 10.16 {py:.2f})) (stroke (width 0)) (uuid "{generate_uuid()}"))')
        sexp.append(f'  (label "PROBE_CH{i}" (at 10.16 {py:.2f} 180) (effects (font (size 1.27 1.27)) (justify right)))')
        # Print PCB alias name as text next to connector
        sexp.append(f'  (label "{ch_names[i]}" (at 33.02 {py:.2f} 0) (effects (font (size 1.27 1.27)) (justify left)))')

    sexp.append(')') # End kicad_sch

    with open(sch_path, "w") as f:
        f.write("\n".join(sexp))
    
    # 3. Simple empty board file (vseq.kicad_pcb) so the project is fully complete
    pcb_path = os.path.join(project_dir, "vseq.kicad_pcb")
    pcb_content = f"""(kicad_pcb (version 20211014) (generator pcbnew)
  (uuid "{generate_uuid()}")
  (paper "A4")
  (title_block
    (title "VSeq Bipolar 10ch Sequencer PCB")
    (company "Antigravity")
  )
)"""
    with open(pcb_path, "w") as f:
        f.write(pcb_content)

    # 4. Copy schematic.pdf into kicad_project if available
    import shutil
    pdf_source = "/Users/noorzoolhilmi/Desktop/vseq/schematic.pdf"
    if os.path.exists(pdf_source):
        shutil.copy2(pdf_source, os.path.join(project_dir, "schematic.pdf"))

    # 5. Re-package kicad_project.zip
    zip_target = "/Users/noorzoolhilmi/Desktop/vseq/kicad_project"
    shutil.make_archive(zip_target, 'zip', "/Users/noorzoolhilmi/Desktop/vseq", "kicad_project")

    print("Successfully generated KiCad CAD project and kicad_project.zip at", project_dir)

if __name__ == "__main__":
    create_kicad_project()
