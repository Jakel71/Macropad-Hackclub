import board
import digitalio
import time

print("\n" + "="*50)
print("MATRIX DIAGNOSE - Finde die richtige Pin-Zuordnung")
print("="*50)

# Aktuelle Pin-Konfiguration
row_pins = [board.RX, board.SCK, board.MISO, board.MOSI]
col_pins = [board.A3, board.SDA, board.SCL, board.TX]

row_names = ["RX/P8", "SCK/P9", "MISO/P10", "MOSI/P11"]
col_names = ["A3/P4", "SDA/P5", "SCL/P6", "TX/P7"]

print("\nAktuelle Konfiguration:")
print("ROWS:", ", ".join(row_names))
print("COLS:", ", ".join(col_names))
print()

# Setup Rows als Output (HIGH = deaktiviert)
rows = []
for i, pin in enumerate(row_pins):
    row = digitalio.DigitalInOut(pin)
    row.direction = digitalio.Direction.OUTPUT
    row.value = True  # HIGH = inaktiv
    rows.append(row)
    print(f"✓ Row {i} ({row_names[i]}): HIGH (inaktiv)")

# Setup Columns als Input mit Pull-Up
cols = []
for i, pin in enumerate(col_pins):
    col = digitalio.DigitalInOut(pin)
    col.direction = digitalio.Direction.INPUT
    col.pull = digitalio.Pull.UP
    cols.append(col)
    print(f"✓ Col {i} ({col_names[i]}): INPUT Pull-UP")

print("\n" + "="*50)
print("LIVE MATRIX SCAN")
print("="*50)
print("\nDrücke EINE Taste und schau, welche erkannt wird!")
print("Format: [Row,Col] = Position in Matrix")
print("STRG+C zum Beenden\n")

# Tracking
last_state = [[False for _ in range(4)] for _ in range(4)]

try:
    while True:
        active_keys = []
        
        # Scanne jede Row
        for row_idx in range(4):
            # Aktiviere nur diese Row (LOW)
            rows[row_idx].value = False
            time.sleep(0.005)  # 5ms Stabilisierung
            
            # Lese alle Columns
            for col_idx in range(4):
                # Pull-Up invertiert: LOW = gedrückt
                is_pressed = not cols[col_idx].value
                
                if is_pressed:
                    key_num = row_idx * 4 + col_idx
                    active_keys.append((row_idx, col_idx, key_num))
            
            # Deaktiviere Row wieder (HIGH)
            rows[row_idx].value = True
            time.sleep(0.001)  # 1ms Pause
        
        # Zeige aktive Tasten
        if active_keys:
            print("\n--- TASTEN GEDRÜCKT ---")
            for row, col, num in active_keys:
                print(f"  [Row {row}, Col {col}] = Taste {num} ({row_names[row]} + {col_names[col]})")
            time.sleep(0.2)  # Debounce
        
        time.sleep(0.01)

except KeyboardInterrupt:
    print("\n\nDiagnose beendet\n")
    
    # Cleanup
    for row in rows:
        row.deinit()
    for col in cols:
        col.deinit()

print("="*50)
print("AUSWERTUNG:")
print("="*50)
print("\nDrücke jede Taste einzeln und notiere:")
print("  - Welche Position wird erkannt?")
print("  - Werden mehrere Positionen erkannt?")
print("  - Ist die Reihenfolge konsistent?")
print("\nDann können wir die Pins richtig zuordnen!")