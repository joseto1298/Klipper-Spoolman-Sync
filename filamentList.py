def parse_gcode(filepath):
    """Escanea el archivo buscando ID de Spoolman, Capa y Altura Z."""
    if os.path.isdir(filepath):
        print(f"ERROR: '{filepath}' es una carpeta.")
        return []

    secuencia = []
    capa_actual = 0
    z_actual = 0.0
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # 1. Detectar Capa
                layer_match = re.search(r"SET_PRINT_STATS_INFO\s+CURRENT_LAYER=(\d+)", line)
                if layer_match:
                    capa_actual = int(layer_match.group(1))

                # 2. Detectar Altura Z (buscando _PLR_Z o G1 Z)
                z_match = re.search(r"(?:_PLR_Z Z=|G1 Z)(\d+\.?\d*)", line)
                if z_match:
                    z_actual = float(z_match.group(1))

                # 3. Detectar ID de Filamento
                match = re.search(r"ASSERT_ACTIVE_FILAMENT\s+ID=(\d+)", line)
                if match:
                    fid = int(match.group(1))
                    
                    # Guardamos el evento con toda la información
                    secuencia.append({
                        "id": fid, 
                        "layer": capa_actual,
                        "z_height": z_actual
                    })
                    
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

    return secuencia

def main():
    # ... (resto del código de inicialización igual) ...
    
    secuencia = parse_gcode(filepath)
    
    if not secuencia:
        print("ℹ️  No se detectaron comandos de filamento en este archivo.")
        return

    print("\n🧵 SECUENCIA DE FILAMENTOS POR ALTURA")
    print("-" * 75)
    print(f"{'#':<3} {'CAPA':<8} {'ALTURA Z':<12} {'ID':<6} {'INFO FILAMENTO'}")
    print("-" * 75)
    
    for i, evento in enumerate(secuencia, start=1):
        info = get_filament_info(evento['id'])
        z_str = f"{evento['z_height']:.2f} mm"
        print(f"{i:<3} {evento['layer']:<8} {z_str:<12} [{evento['id']:^4}] {info['name']} ({info['material']})")
    
    print("-" * 75)
    print("✅ Análisis finalizado.\n")
