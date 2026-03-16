import re, os, sys, configparser, requests

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    try:
        return config.get("Spoolman", "SPOOLMAN_URL"), config.get("Klipper", "GCODE_PATH")
    except:
        return None, "/home/pi/printer_data/gcodes/"

SPOOLMAN_URL, GCODE_PATH = load_config()

def get_filament_info(fid):
    try:
        # Usamos la URL que confirmaste que funciona
        url = f"{SPOOLMAN_URL}{fid}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            vendor = d.get("vendor", {}).get("name", "") if d.get("vendor") else ""
            return f"{vendor} {d.get('name', '???')} ({d.get('material', '???')})".strip()
    except: pass
    return f"ID {fid} (Desconocido)"

def parse_gcode(filepath):
    # Usamos un set para obtener IDs únicos y una lista para la secuencia
    ids_unicos = []
    secuencia_detallada = []
    ultimo_id = None

    with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
        for line in f:
            match = re.search(r"ASSERT_ACTIVE_FILAMENT\s+ID=(\d+)", line)
            if match:
                fid = int(match.group(1))
                if fid not in ids_unicos:
                    ids_unicos.append(fid)
                
                # Para la secuencia, solo guardamos si realmente cambia el ID
                if fid != ultimo_id:
                    secuencia_detallada.append(fid)
                    ultimo_id = fid
    return ids_unicos, secuencia_detallada

def main():
    if len(sys.argv) < 2: return
    filename = sys.argv[1].replace('"', '')
    filepath = os.path.join(GCODE_PATH, filename) if not os.path.isabs(filename) else filename

    if not os.path.exists(filepath):
        print(f"❌ No existe: {filepath}")
        return

    ids, secuencia = parse_gcode(filepath)

    print(f"\n📦 RESUMEN DE MATERIALES REQUERIDOS")
    print("-" * 75)
    print(f"{'ID':<6} {'FILAMENTO'}")
    print("-" * 75)
    for fid in ids:
        print(f"[{fid:^4}] {get_filament_info(fid)}")
    
    print("-" * 75)
    print(f"🔄 TOTAL CAMBIOS DE FILAMENTO: {len(secuencia) - 1}")
    print(f"✅ Análisis finalizado.\n")

if __name__ == "__main__":
    main()
