import re, os, sys, configparser, requests, json

# --- CONFIGURACIÓN ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(BASE_DIR, "config.ini")
CACHE_FILE = 'filament_cache.json'

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_PATH)
    try:
        return config.get("Spoolman", "SPOOLMAN_URL"), config.get("Klipper", "GCODE_PATH")
    except:
        return None, "/home/pi/printer_data/gcodes/"

SPOOLMAN_URL, GCODE_PATH = load_config()

def get_cache_path():
    return os.path.join(BASE_DIR, CACHE_FILE)

def load_cache():
    cache_path = get_cache_path()
    if os.path.exists(cache_path):
        try:
            with open(cache_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_cache(cache):
    cache_path = get_cache_path()
    with open(cache_path, 'w', encoding='utf-8') as f:
        json.dump(cache, f, ensure_ascii=False, indent=2)

def get_filament_info(fid):
    cache = load_cache()
    str_id = str(fid)

    if str_id in cache:
        d = cache[str_id]
        vendor = d.get("vendor", "")
        return f"{vendor} {d.get('name', '???')} ({d.get('material', '???')})".strip()

    try:
        url = f"{SPOOLMAN_URL}{fid}"
        r = requests.get(url, timeout=3)
        if r.status_code == 200:
            d = r.json()
            vendor = d.get("vendor", {}).get("name", "") if d.get("vendor") else ""
            name = d.get("name", "???")
            material = d.get("material", "???")

            cache[str_id] = {"name": name, "material": material, "vendor": vendor}
            save_cache(cache)

            return f"{vendor} {name} ({material})".strip()
    except:
        pass
    return f"ID {fid} (Desconocido)"

def parse_gcode(filepath):
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
    print("-" * 25)
    print(f"{'ID':<6} {'FILAMENTO'}")
    print("-" * 25)
    for fid in ids:
        print(f"[{fid:^4}] {get_filament_info(fid)}")
    
    print("-" * 25)
    print(f"🔄 TOTAL CAMBIOS DE FILAMENTO: {len(secuencia) - 1}")
    print(f"✅ Análisis finalizado.\n")

if __name__ == "__main__":
    main()
