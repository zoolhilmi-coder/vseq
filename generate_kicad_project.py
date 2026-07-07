import os
import uuid
import shutil
import zipfile

def gen_uuid():
    return str(uuid.uuid4())

def create_kicad_project():
    project_dir = "/Users/noorzoolhilmi/Desktop/vseq/kicad_project"
    os.makedirs(project_dir, exist_ok=True)

    # ──────────────────────────────────────────────
    # 1.  vseq.kicad_pro
    # ──────────────────────────────────────────────
    pro_content = """{
  "board": {
    "design_settings": {}
  },
  "libraries": {
    "pinned_footprint_libs": [],
    "pinned_symbol_libs": []
  },
  "meta": {
    "filename": "vseq.kicad_pro",
    "version": 1
  },
  "schematic": {
    "annotate_start_num": 0,
    "drawing": {
      "default_text_size": 1.27
    }
  }
}"""
    with open(os.path.join(project_dir, "vseq.kicad_pro"), "w") as f:
        f.write(pro_content)

    # ──────────────────────────────────────────────
    # 2.  vseq.kicad_sch  (KiCad 7 / version 20230121)
    #
    #  Circuit per channel:
    #   Vin ─── R1(1M) ──┬── R2(100k) ── +3.3V
    #                    │
    #                    ├── R3(120k) ── GND
    #                    │
    #                    ├── D1(3.3V zener cathode) ── GND
    #                    │
    #                    └── U_A(+) ──► U_A(out) ── CH_ADC net
    #
    #  10 channels mapped to STM32 pins PA0-PA7, PB0, PB1
    # ──────────────────────────────────────────────

    CH = 10
    stm32_pins = ["PA0","PA1","PA2","PA3","PA4","PA5","PA6","PA7","PB0","PB1"]
    ch_labels  = ["VCC_12V","VCC_5V","VCC_3V3","TRIGGER","VRM_CORE",
                  "VRAM","V_FAN","VDDCI","PGOOD","VSOC"]

    # Grid step between channels (mm)
    ROW = 30.48

    # X positions for each sub-block
    X_LABEL  = 30.0
    X_R1     = 55.0
    X_VX     = 70.0    # junction node Vx
    X_R2     = 70.0    # same x, goes up
    X_R3     = 70.0    # same x, goes down
    X_D1     = 85.0
    X_OPAMP  = 105.0
    X_OUT    = 125.0
    X_NETLBL = 130.0
    X_STM32  = 200.0

    # Y base for channel 0
    Y0 = 30.0

    lines = []

    def L(s):
        lines.append(s)

    # ── Header ──
    L('(kicad_sch (version 20230121) (generator eeschema)')
    L(f'  (uuid "{gen_uuid()}")')
    L('  (paper "A3" landscape)')

    L('  (title_block')
    L('    (title "VSeq 10-Channel Bipolar Voltage Analyser")')
    L('    (company "Antigravity")')
    L('    (rev "1.3")')
    L('    (date "2026-07-07")')
    L('  )')

    # ── lib_symbols: reference KiCad standard libraries ──
    # KiCad resolves these automatically from the installed symbol libs.
    # We only need to declare the symbols we actually USE.
    L('  (lib_symbols')

    # ── Device:R ──
    L('    (symbol "Device:R" (pin_numbers (hide yes)) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    L('      (property "Reference" "R" (at 1.524 0 90) (effects (font (size 1.27 1.27))))')
    L('      (property "Value" "R" (at -1.524 0 90) (effects (font (size 1.27 1.27))))')
    L('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (symbol "R_0_1"')
    L('        (rectangle (start -1.016 -2.54) (end 1.016 2.54) (stroke (width 0.254) (type default)) (fill (type none)))')
    L('      )')
    L('      (symbol "R_1_1"')
    L('        (pin passive line (at 0 3.81 270) (length 1.27)')
    L('          (name "~" (effects (font (size 1.27 1.27))))')
    L('          (number "1" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('        (pin passive line (at 0 -3.81 90) (length 1.27)')
    L('          (name "~" (effects (font (size 1.27 1.27))))')
    L('          (number "2" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('      )')
    L('    )')

    # ── Device:D_Zener ──
    L('    (symbol "Device:D_Zener" (pin_numbers (hide yes)) (pin_names (offset 0)) (in_bom yes) (on_board yes)')
    L('      (property "Reference" "D" (at 0 2.54 0) (effects (font (size 1.27 1.27))))')
    L('      (property "Value" "D_Zener" (at 0 -2.54 0) (effects (font (size 1.27 1.27))))')
    L('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (symbol "D_Zener_0_1"')
    L('        (polyline (pts (xy 0 -1.27) (xy 0 1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy -1.27 -1.27) (xy 0 0) (xy 1.27 -1.27)) (stroke (width 0.254) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy -1.27 1.27) (xy -1.27 0.635)) (stroke (width 0.254) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy 1.27 1.27) (xy 1.27 1.905)) (stroke (width 0.254) (type default)) (fill (type none)))')
    L('      )')
    L('      (symbol "D_Zener_1_1"')
    L('        (pin passive line (at 0 3.81 270) (length 2.54)')
    L('          (name "K" (effects (font (size 1.27 1.27))))')
    L('          (number "1" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('        (pin passive line (at 0 -3.81 90) (length 2.54)')
    L('          (name "A" (effects (font (size 1.27 1.27))))')
    L('          (number "2" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('      )')
    L('    )')

    # ── Amplifier_Operational:TLV2371 (single rail-to-rail opamp) ──
    L('    (symbol "Amplifier_Operational:TLV2371" (pin_names (offset 0.254)) (in_bom yes) (on_board yes)')
    L('      (property "Reference" "U" (at 5.08 5.08 0) (effects (font (size 1.27 1.27))))')
    L('      (property "Value" "TLV2371" (at 5.08 -5.08 0) (effects (font (size 1.27 1.27))))')
    L('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Datasheet" "~" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (symbol "TLV2371_0_1"')
    L('        (polyline (pts (xy -5.08 5.08) (xy -5.08 -5.08) (xy 5.08 0) (xy -5.08 5.08)) (stroke (width 0.254) (type default)) (fill (type background)))')
    L('      )')
    L('      (symbol "TLV2371_1_1"')
    L('        (pin input line (at -7.62 2.54 0) (length 2.54)')
    L('          (name "+" (effects (font (size 1.27 1.27))))')
    L('          (number "3" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('        (pin input line (at -7.62 -2.54 0) (length 2.54)')
    L('          (name "-" (effects (font (size 1.27 1.27))))')
    L('          (number "2" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('        (pin output line (at 7.62 0 180) (length 2.54)')
    L('          (name "~" (effects (font (size 1.27 1.27))))')
    L('          (number "1" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('        (pin power_in line (at 0 7.62 270) (length 2.54)')
    L('          (name "VCC" (effects (font (size 1.27 1.27))))')
    L('          (number "5" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('        (pin power_in line (at 0 -7.62 90) (length 2.54)')
    L('          (name "GND" (effects (font (size 1.27 1.27))))')
    L('          (number "4" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('      )')
    L('    )')

    # ── power:GND ──
    L('    (symbol "power:GND" (power) (pin_names (offset 0)) (in_bom no) (on_board no)')
    L('      (property "Reference" "#PWR" (at 0 -1.27 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Value" "GND" (at 0 -3.81 0) (effects (font (size 1.27 1.27))))')
    L('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (symbol "GND_0_1"')
    L('        (polyline (pts (xy 0 0) (xy 0 -1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy -1.27 -1.27) (xy 1.27 -1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy -0.762 -1.905) (xy 0.762 -1.905)) (stroke (width 0) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy -0.254 -2.54) (xy 0.254 -2.54)) (stroke (width 0) (type default)) (fill (type none)))')
    L('      )')
    L('      (symbol "GND_1_1"')
    L('        (pin power_in line (at 0 0 270) (length 0) (hide yes)')
    L('          (name "GND" (effects (font (size 1.27 1.27))))')
    L('          (number "1" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('      )')
    L('    )')

    # ── power:+3.3V ──
    L('    (symbol "power:+3.3V" (power) (pin_names (offset 0)) (in_bom no) (on_board no)')
    L('      (property "Reference" "#PWR" (at 0 1.27 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Value" "+3.3V" (at 0 3.556 0) (effects (font (size 1.27 1.27))))')
    L('      (property "Footprint" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (property "Datasheet" "" (at 0 0 0) (effects (font (size 1.27 1.27)) (hide yes)))')
    L('      (symbol "+3.3V_0_1"')
    L('        (polyline (pts (xy 0 0) (xy 0 1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    L('        (polyline (pts (xy -0.762 1.27) (xy 0 2.032) (xy 0.762 1.27)) (stroke (width 0) (type default)) (fill (type none)))')
    L('      )')
    L('      (symbol "+3.3V_1_1"')
    L('        (pin power_in line (at 0 0 90) (length 0) (hide yes)')
    L('          (name "+3.3V" (effects (font (size 1.27 1.27))))')
    L('          (number "1" (effects (font (size 1.27 1.27))))')
    L('        )')
    L('      )')
    L('    )')

    L('  )')  # end lib_symbols

    # ── Sheet-level global power symbols ──
    # One GND bus and one +3.3V bus that all channels share
    def pwr_sym(lib_id, x, y, ref, val):
        L(f'  (symbol (lib_id "{lib_id}") (at {x} {y} 0) (unit 1)')
        L( '    (in_bom no) (on_board no)')
        L(f'    (uuid "{gen_uuid()}")')
        L(f'    (property "Reference" "{ref}" (at {x} {y-2.54:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Value" "{val}" (at {x} {y+2.54:.2f} 0) (effects (font (size 1.27 1.27))))')
        L(f'    (property "Footprint" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Datasheet" "" (at {x} {y} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L( '  )')

    # ── Draw 10 channels ──
    for i in range(CH):
        y = Y0 + i * ROW

        # ---------- net label (probe input) ----------
        L(f'  (global_label "{ch_labels[i]}_IN" (shape input) (at {X_LABEL:.2f} {y:.2f} 0) (fields_autoplaced yes)')
        L( '    (effects (font (size 1.27 1.27)) (justify left))')
        L(f'    (uuid "{gen_uuid()}")')
        L( '  )')

        # wire from label to R1
        L(f'  (wire (pts (xy {X_LABEL:.2f} {y:.2f}) (xy {X_R1-2.54:.2f} {y:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # ---------- R1 (1MΩ, horizontal, series input) ----------
        r1 = f"R{i*3+1}"
        L(f'  (symbol (lib_id "Device:R") (at {X_R1:.2f} {y:.2f} 90) (unit 1)')
        L( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        L(f'    (uuid "{gen_uuid()}")')
        L(f'    (property "Reference" "{r1}" (at {X_R1:.2f} {y-3.048:.2f} 90) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Value" "1M" (at {X_R1:.2f} {y+3.048:.2f} 90) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {X_R1:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Datasheet" "~" (at {X_R1:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L( '  )')

        # wire R1 right pin → Vx
        L(f'  (wire (pts (xy {X_R1+3.81:.2f} {y:.2f}) (xy {X_VX:.2f} {y:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # junction at Vx
        L(f'  (junction (at {X_VX:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{gen_uuid()}"))')

        # ---------- R2 (100kΩ, vertical, up to +3.3V) ----------
        r2 = f"R{i*3+2}"
        vx = X_VX
        r2y = y - 6.35   # centre of R2
        L(f'  (symbol (lib_id "Device:R") (at {vx:.2f} {r2y:.2f} 0) (unit 1)')
        L( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        L(f'    (uuid "{gen_uuid()}")')
        L(f'    (property "Reference" "{r2}" (at {vx+3.048:.2f} {r2y:.2f} 0) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Value" "100k" (at {vx-3.048:.2f} {r2y:.2f} 0) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {vx:.2f} {r2y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Datasheet" "~" (at {vx:.2f} {r2y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L( '  )')

        # wire Vx up to R2 pin 2
        L(f'  (wire (pts (xy {vx:.2f} {y:.2f}) (xy {vx:.2f} {r2y+3.81:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        # +3.3V power above R2
        pwr_sym("power:+3.3V", vx, r2y-3.81-1.27, "#PWR0"+str(i*4+1).zfill(2), "+3.3V")
        # wire R2 top pin → +3.3V
        L(f'  (wire (pts (xy {vx:.2f} {r2y-3.81:.2f}) (xy {vx:.2f} {r2y-3.81-1.27:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # ---------- R3 (120kΩ, vertical, down to GND) ----------
        r3 = f"R{i*3+3}"
        r3y = y + 6.35
        L(f'  (symbol (lib_id "Device:R") (at {vx:.2f} {r3y:.2f} 0) (unit 1)')
        L( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        L(f'    (uuid "{gen_uuid()}")')
        L(f'    (property "Reference" "{r3}" (at {vx+3.048:.2f} {r3y:.2f} 0) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Value" "120k" (at {vx-3.048:.2f} {r3y:.2f} 0) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Footprint" "Resistor_SMD:R_0805_2012Metric" (at {vx:.2f} {r3y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Datasheet" "~" (at {vx:.2f} {r3y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L( '  )')

        # wire Vx down to R3 pin 1
        L(f'  (wire (pts (xy {vx:.2f} {y:.2f}) (xy {vx:.2f} {r3y-3.81:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        # GND power below R3
        pwr_sym("power:GND", vx, r3y+3.81+1.27, "#PWR0"+str(i*4+2).zfill(2), "GND")
        L(f'  (wire (pts (xy {vx:.2f} {r3y+3.81:.2f}) (xy {vx:.2f} {r3y+3.81+1.27:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # ---------- D1 (3.3V Zener, K up at Vx, A down to GND) ----------
        d1 = f"D{i+1}"
        dx = X_D1
        L(f'  (symbol (lib_id "Device:D_Zener") (at {dx:.2f} {y:.2f} 270) (unit 1)')
        L( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        L(f'    (uuid "{gen_uuid()}")')
        L(f'    (property "Reference" "{d1}" (at {dx+3.048:.2f} {y:.2f} 90) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Value" "3V3" (at {dx-3.048:.2f} {y:.2f} 90) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Footprint" "Diode_SMD:D_SOD-123" (at {dx:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Datasheet" "~" (at {dx:.2f} {y:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L( '  )')

        # wire Vx → D1 cathode (pin 1)
        L(f'  (wire (pts (xy {vx:.2f} {y:.2f}) (xy {dx-3.81:.2f} {y:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        # junction at Vx-D wire start (already have junction at vx)
        # D1 anode → GND below
        L(f'  (wire (pts (xy {dx:.2f} {y+3.81:.2f}) (xy {dx:.2f} {y+5.08:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        pwr_sym("power:GND", dx, y+5.08+1.27, "#PWR0"+str(i*4+3).zfill(2), "GND")

        # ---------- U (TLV2371 op-amp buffer) ----------
        ux = X_OPAMP
        uy = y
        u_ref = f"U{i+1}"
        L(f'  (symbol (lib_id "Amplifier_Operational:TLV2371") (at {ux:.2f} {uy:.2f} 0) (unit 1)')
        L( '    (in_bom yes) (on_board yes) (fields_autoplaced yes)')
        L(f'    (uuid "{gen_uuid()}")')
        L(f'    (property "Reference" "{u_ref}" (at {ux+7.62:.2f} {uy-6.35:.2f} 0) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Value" "TLV2371" (at {ux+7.62:.2f} {uy-3.81:.2f} 0) (effects (font (size 1.016 1.016))))')
        L(f'    (property "Footprint" "Package_TO_SOT_THT:SOT-23-5" (at {ux:.2f} {uy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L(f'    (property "Datasheet" "~" (at {ux:.2f} {uy:.2f} 0) (effects (font (size 1.27 1.27)) (hide yes)))')
        L( '  )')

        # VCC (pin 5) → +3.3V, GND (pin 4) → GND
        pwr_sym("power:+3.3V", ux, uy-7.62-2.54, "#PWR0"+str(i*4+4+1).zfill(2), "+3.3V")
        L(f'  (wire (pts (xy {ux:.2f} {uy-7.62:.2f}) (xy {ux:.2f} {uy-7.62-2.54:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        pwr_sym("power:GND", ux, uy+7.62+1.27, "#PWR0"+str(i*4+5+1).zfill(2), "GND")
        L(f'  (wire (pts (xy {ux:.2f} {uy+7.62:.2f}) (xy {ux:.2f} {uy+7.62+1.27:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # wire Vx → op-amp (+) input at (ux-7.62, uy+2.54)
        # D1 right side connects to Vx at x=dx, y=y; go right to opamp
        L(f'  (wire (pts (xy {dx+3.81:.2f} {y:.2f}) (xy {ux-7.62:.2f} {y:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        # junction between D wire and opamp input
        L(f'  (junction (at {dx+3.81:.2f} {y:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{gen_uuid()}"))')
        # move from main y to pin y+2.54
        L(f'  (wire (pts (xy {ux-7.62:.2f} {y:.2f}) (xy {ux-7.62:.2f} {uy+2.54:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # feedback: output (ux+7.62, uy) → (−) input (ux-7.62, uy-2.54) via loop
        fb_x = ux + 10.16
        L(f'  (wire (pts (xy {ux+7.62:.2f} {uy:.2f}) (xy {fb_x:.2f} {uy:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        L(f'  (wire (pts (xy {fb_x:.2f} {uy:.2f}) (xy {fb_x:.2f} {uy-2.54:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        fb_inner_x = ux - 7.62
        L(f'  (wire (pts (xy {fb_x:.2f} {uy-2.54:.2f}) (xy {fb_inner_x:.2f} {uy-2.54:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')

        # junction at output
        L(f'  (junction (at {ux+7.62:.2f} {uy:.2f}) (diameter 0) (color 0 0 0 0) (uuid "{gen_uuid()}"))')

        # net label on output
        L(f'  (net_tie (net_names ("{ch_labels[i]}_ADC" "CH{i}_ADC")) (at {X_OUT:.2f} {uy:.2f}) (uuid "{gen_uuid()}"))')
        L(f'  (wire (pts (xy {ux+7.62:.2f} {uy:.2f}) (xy {X_OUT:.2f} {uy:.2f})) (stroke (width 0) (type default)) (uuid "{gen_uuid()}"))')
        L(f'  (global_label "CH{i}_ADC" (shape output) (at {X_NETLBL:.2f} {uy:.2f} 0) (fields_autoplaced yes)')
        L( '    (effects (font (size 1.27 1.27)) (justify left))')
        L(f'    (uuid "{gen_uuid()}")')
        L( '  )')

    # ── STM32 connector block on right ──
    cx = X_STM32
    L(f'  (text "STM32 ADC Inputs" (at {cx+5:.2f} {Y0-10:.2f} 0) (effects (font (size 2.032 2.032) (bold yes))))')
    for i in range(CH):
        uy = Y0 + i * ROW
        L(f'  (global_label "CH{i}_ADC" (shape input) (at {cx:.2f} {uy:.2f} 180) (fields_autoplaced yes)')
        L( '    (effects (font (size 1.27 1.27)) (justify right))')
        L(f'    (uuid "{gen_uuid()}")')
        L( '  )')
        L(f'  (text "{stm32_pins[i]}" (at {cx+15:.2f} {uy:.2f} 0) (effects (font (size 1.27 1.27))))')

    L(')')  # end kicad_sch

    sch_path = os.path.join(project_dir, "vseq.kicad_sch")
    with open(sch_path, "w") as f:
        f.write("\n".join(lines))

    # ──────────────────────────────────────────────
    # 3.  vseq.kicad_pcb  (KiCad 7 minimal valid)
    # ──────────────────────────────────────────────
    pcb_content = """(kicad_pcb (version 20221018) (generator pcbnew)
  (general
    (thickness 1.6)
    (legacy_teardrops no)
  )
  (paper "A4")
  (title_block
    (title "VSeq Bipolar 10ch Sequencer PCB")
    (company "Antigravity")
  )
  (layers
    (0 "F.Cu" signal)
    (31 "B.Cu" signal)
    (32 "B.Adhes" user "B.Adhesive")
    (33 "F.Adhes" user "F.Adhesive")
    (34 "B.Paste" user)
    (35 "F.Paste" user)
    (36 "B.SilkS" user "B.Silkscreen")
    (37 "F.SilkS" user "F.Silkscreen")
    (38 "B.Mask" user)
    (39 "F.Mask" user)
    (40 "Dwgs.User" user "User.Drawings")
    (41 "Cmts.User" user "User.Comments")
    (42 "Eco1.User" user "User.Eco1")
    (43 "Eco2.User" user "User.Eco2")
    (44 "Edge.Cuts" user)
    (45 "Margin" user)
    (46 "B.CrtYd" user "B.Courtyard")
    (47 "F.CrtYd" user "F.Courtyard")
    (48 "B.Fab" user)
    (49 "F.Fab" user)
  )
  (setup
    (pad_to_mask_clearance 0)
    (smd_soldermask_margin 0)
    (pcbplotparams
      (layerselection 0x00010fc_ffffffff)
      (plot_on_all_layers_selection 0x0000000_00000000)
      (disableapertmacros no)
      (usegerberextensions no)
      (usegerberattributes yes)
      (usegerberadvancedattributes yes)
      (creategerberjobfile yes)
      (dashed_line_dash_ratio 12.0)
      (dashed_line_gap_ratio 3.0)
      (svguseinch no)
      (svgprecision 4)
      (excludeedgelayer yes)
      (plotframeref no)
      (viasonmask no)
      (mode 1)
      (useauxorigin no)
      (hpglpennumber 1)
      (hpglpenspeed 20)
      (hpglpendiameter 15.0)
      (pdf_front_fp_property_popups yes)
      (pdf_back_fp_property_popups yes)
      (dxfpolygonmode yes)
      (dxfimperialunits yes)
      (dxfusepcbnewfont yes)
      (psnegative no)
      (psa4output no)
      (plotreference yes)
      (plotvalue yes)
      (plotfptext yes)
      (plotinvisibletext no)
      (sketchpadsonfab no)
      (subtractmaskfromsilk no)
      (outputformat 1)
      (mirror no)
      (drillshape 1)
      (scaleselection 1)
      (outputdirectory "")
    )
  )
  (net 0 "")
)
"""
    with open(os.path.join(project_dir, "vseq.kicad_pcb"), "w") as f:
        f.write(pcb_content)

    # ──────────────────────────────────────────────
    # 4.  Copy schematic.pdf and re-zip
    # ──────────────────────────────────────────────
    pdf_src = "/Users/noorzoolhilmi/Desktop/vseq/schematic.pdf"
    pdf_dst = os.path.join(project_dir, "schematic.pdf")
    if os.path.exists(pdf_src):
        shutil.copy2(pdf_src, pdf_dst)

    zip_path = "/Users/noorzoolhilmi/Desktop/vseq/kicad_project.zip"
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(project_dir):
            # skip lock files and hidden dirs
            dirs[:] = [d for d in dirs if not d.startswith(".")]
            for fname in files:
                if fname.endswith(".lck") or fname.startswith("."):
                    continue
                fpath = os.path.join(root, fname)
                arcname = os.path.relpath(fpath, "/Users/noorzoolhilmi/Desktop/vseq")
                zf.write(fpath, arcname)

    print(f"Done. Files in {project_dir}:")
    for f in os.listdir(project_dir):
        print(" ", f)

if __name__ == "__main__":
    create_kicad_project()
