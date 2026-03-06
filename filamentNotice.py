#!/home/pi/klipper_filament/venv/bin/python3
import sys, requests, os, configparser

# Cargamos config lo más rápido posible
def main():
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config = configparser.ConfigParser()
        config.read(os.path.join(script_dir, 'config.ini'))
        
        spool_url = config['Spoolman']['SPOOLMAN_URL']
        moon_url = config['Moonraker']['MOONRAKER_URL']
        if not moon_url.endswith('/'): moon_url += '/'
        
        fid = sys.argv[1]
        motivo = sys.argv[2]

        # 1. Petición a Spoolman (Timeout agresivo de 2s)
        name, mat = "Unknown", "Unknown"
        if fid != "0":
            try:
                r = requests.get(f"{spool_url.rstrip('/')}/filament/{fid}", timeout=2)
                data = r.json()
                name, mat = data.get("name"), data.get("material")
            except: pass

        # 2. Respuesta única a Moonraker (Abrir el menú)
        # Enviamos un solo POST con todo para no saturar el bus serie
        gcode = f'_FILAMENT_INFO ID={fid} NAME="{name}" MATERIAL="{mat}" MOTIVO="{motivo}"'
        requests.post(f"{moon_url}printer/gcode/script", json={"script": gcode}, timeout=1)

    except:
        sys.exit(1)

if __name__ == "__main__":
    main()
