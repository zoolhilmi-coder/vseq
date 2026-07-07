"""
generate_kicad_project.py
Generates a valid KiCad 7 project for VSeq 10-channel bipolar voltage analyser.
Circuit per channel:
  Vin --R1(1M)--+--R2(100k)--+3.3V
                |
                +--R3(120k)--GND
                |
                +--D1(Zener 3V3)--GND
                |
                +--(+)TLV2371(out)--CHx_ADC net label
                    (-)----+
"""
import os, uuid, shutil, zipfile, subprocess

def g():
    return str(uuid.uuid4())

def run():
    OUT = "/Users/noorzoolhilmi/Desktop/vseq/kicad_project"
    os.makedirs(OUT, exist_ok=True)

    # ── 1. vseq.kicad_pro ────────────────────────────────────────────────────
    with open(f"{OUT}/vseq.kicad_pro", "w") as f:
        f.write('{\n'
                '  "meta": { "filename": "vseq.kicad_pro", "version": 1 },\n'
                '  "schematic": { "annotate_start_num": 0 }\n'
                '}\n')

    # ── 2. vseq.kicad_sch ────────────────────────────────────────────────────
    CH        = 10
    STM32     = ["PA0","PA1","PA2","PA3","PA4","PA5","PA6","PA7","PB0","PB1"]
    CH_LABELS = ["VCC_12V","VCC_5V","VCC_3V3","TRIGGER","VRM_CORE",
                 "VRAM","V_FAN","VDDCI","PGOOD","VSOC"]
    ROW       = 35.0     # mm between channels

    # Column X positions
    X_IN   = 20.0   # input global label
    X_R1   = 42.0   # R1 centre
    X_VX   = 55.0   # Vx junction
    X_D1   = 68.0   # Zener
    X_OP   = 88.0   # op-amp centre
    X_OUT  = 107.0  # output global label
    X_STM  = 180.0  # STM32 side global labels
    Y0     = 25.0   # first channel y

    sch = []
    def S(s): sch.append(s)

    # ── Header ──
    S(f'(kicad_sch (version 20230121) (generator eeschema)')
    S(f'  (uuid "{g()}")')
    S(f'  (paper "A3")')
    S(f'  (title_block')
    S(f'    (title "VSeq 10-Channel Bipolar Voltage Analyser")')
    S(f'    (company "Antigravity")')
    S(f'    (rev "1.4")')
    S(f'    (date "2026-07-07")')
    S(f'  )')

    # ── lib_symbols ──
    S('  (lib_symbols')

    # Device:R
    S('    (symbol "Device:R" (pin_numbers (hide yes)) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    S('      (property "Reference" "R" (at 1.524 0 90) (effects (font (size 1.27 1.27))))')
    S('      (property "Value" "R" (at -1.524 0 90) (effects (font (size 1.27 1.27))))')
    S('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (symbol "R_0_1"')
    S('        (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none)))')
    S('      )')
    S('      (symbol "R_1_1"')
    S('        (pin passive line (at 0 3.81 270) (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    S('        (pin passive line (at 0 -3.81 90)  (length 1.27) (name "~" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    S('      )')
    S('    )')

    # Device:D_Zener
    S('    (symbol "Device:D_Zener" (pin_numbers (hide yes)) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    S('      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))')
    S('      (property "Value" "D_Zener" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))')
    S('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (symbol "D_Zener_0_1"')
    S('        (polyline (pts (xy 0 -1.27) (xy 0 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy -1.27 -1.27) (xy 0 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy -1.27 1.27) (xy -1.27 0.508)) (stroke (width 0.254) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy 1.27 1.27) (xy 1.27 1.905)) (stroke (width 0.254) (type default)) (fill (type none)))')
    S('      )')
    S('      (symbol "D_Zener_1_1"')
    S('        (pin passive line (at 0 3.81 270) (length 2.54) (name "K" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    S('        (pin passive line (at 0 -3.81 90)  (length 2.54) (name "A" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    S('      )')
    S('    )')

    # Amplifier_Operational:TLV2371 (single op-amp, rail-to-rail)
    S('    (symbol "Amplifier_Operational:TLV2371" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    S('      (property "Reference" "U" (at 5.08 5.08 0) (effects (font (size 1.27 1.27))))')
    S('      (property "Value" "TLV2371" (at 5.08 -5.08 0) (effects (font (size 1.27 1.27))))')
    S('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (symbol "TLV2371_0_1"')
    S('        (polyline (pts (xy -5.08 5.08) (xy -5.08 -5.08) (xy 5.08 0) (xy -5.08 5.08)) (stroke (width 0.254) (type default)) (fill (type background)))')
    S('      )')
    S('      (symbol "TLV2371_1_1"')
    S('        (pin input line (at -7.62 2.54 0) (length 2.54) (name "+" (effects (font (size 1.27 1.27)))) (number "3" (effects (font (size 1.27 1.27)))))')
    S('        (pin input line (at -7.62 -2.54 0) (length 2.54) (name "-" (effects (font (size 1.27 1.27)))) (number "2" (effects (font (size 1.27 1.27)))))')
    S('        (pin output line (at 7.62 0 180) (length 2.54) (name "~" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    S('        (pin power_in line (at 0 7.62 270) (length 2.54) (name "VCC" (effects (font (size 1.27 1.27)))) (number "5" (effects (font (size 1.27 1.27)))))')
    S('        (pin power_in line (at 0 -7.62 90) (length 2.54) (name "GND" (effects (font (size 1.27 1.27)))) (number "4" (effects (font (size 1.27 1.27)))))')
    S('      )')
    S('    )')

    # power:GND
    S('    (symbol "power:GND" (power) (pin_names (offset 0)) (in_bom no) (on_board no)')
    S('      (property "Reference" "#PWR" (at 0 -1.27 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))')
    S('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (symbol "GND_0_1"')
    S('        (polyline (pts (xy 0 0) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy -0.762 -1.905) (xy 0.762 -1.905)) (stroke (width 0) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy -0.254 -2.54) (xy 0.254 -2.54)) (stroke (width 0) (type default)) (fill (type none)))')
    S('      )')
    S('      (symbol "GND_1_1"')
    S('        (pin power_in line (at 0 0 270) (length 0) (hide yes) (name "GND" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    S('      )')
    S('    )')

    # power:+3.3V
    S('    (symbol "power:+3.3V" (power) (pin_names (offset 0)) (in_bom no) (on_board no)')
    S('      (property "Reference" "#PWR" (at 0 1.27 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Value" "+3.3V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))')
    S('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    S('      (symbol "+3.3V_0_1"')
    S('        (polyline (pts (xy 0 0) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    S('        (polyline (pts (xy -0.762 1.27) (xy 0 2.032) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    S('      )')
    S('      (symbol "+3.3V_1_1"')
    S('        (pin power_in line (at 0 0 90) (length 0) (hide yes) (name "+3.3V" (effects (font (size 1.27 1.27)))) (number "1" (effects (font (size 1.27 1.27)))))')
    S('      )')
    S('    )')

    S('  )')  # end lib_symbols

    # ── Helper: place a power symbol (GND or +3.3V) ──
    pwr_idx = [0]
    def pwr(lib, x, y, val):
        pwr_idx[0] += 1
        ref = f"#PWR{pwr_idx[0]:03d}"
        angle = 0
        S(f'  (symbol (lib_id "{lib}") (at {x:.3f} {y:.3f} {angle}) (unit 1)')
        S( '    (in_bom no) (on_board no)')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Reference" "{ref}" (at {x:.3f} {y-2.0:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Value" "{val}" (at {x:.3f} {y+2.0:.3f} 0) (effects (font (size 1.27 1.27))))')
        S(f'    (property "Footprint" "" (at {x:.3f} {y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Datasheet" "" (at {x:.3f} {y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')

    def wire(x1, y1, x2, y2):
        S(f'  (wire (pts (xy {x1:.3f} {y1:.3f}) (xy {x2:.3f} {y2:.3f})) (stroke (width 0) (type default)) (uuid "{g()}"))')

    def junc(x, y):
        S(f'  (junction (at {x:.3f} {y:.3f}) (diameter 0) (color 0 0 0 0) (uuid "{g()}"))')

    def glabel(name, shape, x, y, angle):
        S(f'  (global_label "{name}" (shape {shape}) (at {x:.3f} {y:.3f} {angle}) (fields_autoplaced yes)')
        S( '    (effects (font (size 1.27 1.27)) (justify left))')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Intersheet References" "${{INTERSHEET_REFS}}" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')

    # ── Place 10 channels ──
    sym_instances = []

    for i in range(CH):
        y = Y0 + i * ROW

        # ── Input global label ──
        glabel(f"{CH_LABELS[i]}_IN", "input", X_IN, y, 0)
        wire(X_IN + 9.0, y, X_R1 - 3.81, y)   # gap: global_label tail + R1 pin1

        # ── R1 (1MΩ) horizontal ──
        r1 = f"R{i*3+1}"
        S(f'  (symbol (lib_id "Device:R") (at {X_R1:.3f} {y:.3f} 90) (unit 1)')
        S( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Reference" "{r1}" (at {X_R1:.3f} {y-3.3:.3f} 90) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Value" "1M" (at {X_R1:.3f} {y+3.3:.3f} 90) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {X_R1:.3f} {y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Datasheet" "~" (at {X_R1:.3f} {y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')
        sym_instances.append((r1, "Device", "R", 1, X_R1, y))

        # wire R1 out → Vx
        wire(X_R1 + 3.81, y, X_VX, y)
        junc(X_VX, y)

        # ── R2 (100kΩ) vertical, goes UP to +3.3V ──
        r2 = f"R{i*3+2}"
        r2y = y - 6.0
        S(f'  (symbol (lib_id "Device:R") (at {X_VX:.3f} {r2y:.3f} 0) (unit 1)')
        S( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Reference" "{r2}" (at {X_VX+3.3:.3f} {r2y:.3f} 0) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Value" "100k" (at {X_VX-3.3:.3f} {r2y:.3f} 0) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {X_VX:.3f} {r2y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Datasheet" "~" (at {X_VX:.3f} {r2y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')
        sym_instances.append((r2, "Device", "R", 1, X_VX, r2y))
        wire(X_VX, y, X_VX, r2y + 3.81)
        pwr("power:+3.3V", X_VX, r2y - 3.81 - 1.27, "+3.3V")
        wire(X_VX, r2y - 3.81, X_VX, r2y - 3.81 - 1.27)

        # ── R3 (120kΩ) vertical, goes DOWN to GND ──
        r3 = f"R{i*3+3}"
        r3y = y + 6.0
        S(f'  (symbol (lib_id "Device:R") (at {X_VX:.3f} {r3y:.3f} 0) (unit 1)')
        S( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Reference" "{r3}" (at {X_VX+3.3:.3f} {r3y:.3f} 0) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Value" "120k" (at {X_VX-3.3:.3f} {r3y:.3f} 0) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {X_VX:.3f} {r3y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Datasheet" "~" (at {X_VX:.3f} {r3y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')
        sym_instances.append((r3, "Device", "R", 1, X_VX, r3y))
        wire(X_VX, y, X_VX, r3y - 3.81)
        pwr("power:GND", X_VX, r3y + 3.81 + 1.27, "GND")
        wire(X_VX, r3y + 3.81, X_VX, r3y + 3.81 + 1.27)

        # ── D1 (Zener 3.3V) rotated 270°, K up at Vx, A down ──
        d1 = f"D{i+1}"
        dx = X_D1
        S(f'  (symbol (lib_id "Device:D_Zener") (at {dx:.3f} {y:.3f} 270) (unit 1)')
        S( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Reference" "{d1}" (at {dx+3.3:.3f} {y:.3f} 90) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Value" "3V3" (at {dx-3.3:.3f} {y:.3f} 90) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Footprint" "Diode_SMD:D_SOD-123" (at {dx:.3f} {y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Datasheet" "~" (at {dx:.3f} {y:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')
        sym_instances.append((d1, "Device", "D_Zener", 1, dx, y))
        wire(X_VX, y, dx - 3.81, y)  # Vx → K (cathode, pin1)
        wire(dx + 3.81, y, dx + 3.81 + 1.27, y)  # A (anode, pin2) → GND short
        pwr("power:GND", dx + 3.81 + 1.27, y, "GND")

        # ── U (TLV2371 op-amp buffer) ──
        ux = X_OP
        uy = y
        u_ref = f"U{i+1}"
        S(f'  (symbol (lib_id "Amplifier_Operational:TLV2371") (at {ux:.3f} {uy:.3f} 0) (unit 1)')
        S( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        S(f'    (uuid "{g()}")')
        S(f'    (property "Reference" "{u_ref}" (at {ux+8:.3f} {uy-6:.3f} 0) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Value" "TLV2371" (at {ux+8:.3f} {uy-3.8:.3f} 0) (effects (font (size 1.016 1.016))))')
        S(f'    (property "Footprint" "Package_TO_SOT_THT:SOT-23-5" (at {ux:.3f} {uy:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S(f'    (property "Datasheet" "~" (at {ux:.3f} {uy:.3f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        S( '  )')
        sym_instances.append((u_ref, "Amplifier_Operational", "TLV2371", 1, ux, uy))

        # VCC pin (5) → +3.3V (pin is at ux, uy-7.62)
        pwr("power:+3.3V", ux, uy - 7.62 - 2.54, "+3.3V")
        wire(ux, uy - 7.62, ux, uy - 7.62 - 2.54)
        # GND pin (4) → GND (pin is at ux, uy+7.62)
        pwr("power:GND", ux, uy + 7.62 + 2.54, "GND")
        wire(ux, uy + 7.62, ux, uy + 7.62 + 2.54)

        # Vx → op-amp (+) input pin 3 at (ux-7.62, uy+2.54)
        wire(dx + 3.81 + 1.27, y, ux - 7.62, y)          # horizontal to ux edge
        wire(ux - 7.62, y, ux - 7.62, uy + 2.54)          # drop down to (+) pin
        junc(dx + 3.81 + 1.27, y)

        # Feedback: output pin 1 (ux+7.62, uy) → (−) input pin 2 (ux-7.62, uy-2.54)
        fb_x = ux + 10.0
        wire(ux + 7.62, uy, fb_x, uy)
        wire(fb_x, uy, fb_x, uy - 2.54)
        wire(fb_x, uy - 2.54, ux - 7.62, uy - 2.54)
        junc(ux + 7.62, uy)

        # Output net label
        wire(ux + 7.62, uy, X_OUT - 9.0, uy)
        glabel(f"CH{i}_ADC", "output", X_OUT, uy, 0)

    # ── STM32 side labels ──
    S(f'  (text "STM32 ADC" (at {X_STM+5:.1f} {Y0-12:.1f} 0) (effects (font (size 2.54 2.54) (bold yes))))')
    for i in range(CH):
        uy = Y0 + i * ROW
        glabel(f"CH{i}_ADC", "input", X_STM, uy, 180)
        S(f'  (text "{STM32[i]}" (at {X_STM+15:.1f} {uy:.1f} 0) (effects (font (size 1.27 1.27))))')

    # ── symbol_instances (required by KiCad 7) ──
    S('  (symbol_instances')
    path = f'/{g()}'
    for (ref, lib, sym, unit, x, y) in sym_instances:
        S(f'    (path "{path}"')
        S(f'      (reference "{ref}") (unit {unit}) (value "{sym}") (footprint "")')
        S( '    )')
    S('  )')

    S(')')  # end kicad_sch

    with open(f"{OUT}/vseq.kicad_sch", "w") as f:
        f.write("\n".join(sch) + "\n")

    # ── 3. vseq.kicad_pcb (minimal valid KiCad 7 PCB) ────────────────────────
    # Stripped to only tokens that are universally valid across KiCad 6/7/8
    pcb = """(kicad_pcb (version 20221018) (generator pcbnew)
  (general
    (thickness 1.6)
  )
  (paper "A4")
  (title_block
    (title "VSeq Bipolar 10ch Sequencer PCB")
    (company "Antigravity")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (pad_to_mask_clearance 0)
  )
  (net 0 "")
)
"""
    with open(f"{OUT}/vseq.kicad_pcb", "w") as f:
        f.write(pcb)

    # ── 4. Copy schematic.pdf + create ZIP ───────────────────────────────────
    pdf_src = "/Users/noorzoolhilmi/Desktop/vseq/schematic.pdf"
    if os.path.exists(pdf_src):
        shutil.copy2(pdf_src, f"{OUT}/schematic.pdf")

    # ── Run kicad-cli upgrade to convert to latest KiCad format ──
    KICAD_CLI = "/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli"
    sch_path = f"{OUT}/vseq.kicad_sch"
    pcb_path = f"{OUT}/vseq.kicad_pcb"
    if os.path.exists(KICAD_CLI):
        result = subprocess.run(
            [KICAD_CLI, "sch", "upgrade", "--force", sch_path],
            capture_output=True, text=True
        )
        if "Successfully" in result.stdout:
            print("✓ Schematic upgraded to latest KiCad format")
        else:
            print("⚠ SCH upgrade:", result.stderr[-200:] if result.stderr else result.stdout[-200:])
    else:
        print("⚠ kicad-cli not found, skipping upgrade")

    # ── Re-zip after upgrade (upgraded file may have different content) ──
    zip_path = "/Users/noorzoolhilmi/Desktop/vseq/kicad_project.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(OUT):
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fname in files:
                if fname.endswith(".lck") or fname.startswith("."):
                    continue
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, "/Users/noorzoolhilmi/Desktop/vseq")
                zf.write(fpath, arcname)

    print("Done. Files generated:")
    for f in sorted(os.listdir(OUT)):
        if not f.startswith(".") and not f.endswith(".lck"):
            print(" ", f)

if __name__ == "__main__":
    run()

