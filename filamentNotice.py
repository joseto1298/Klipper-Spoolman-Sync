#!/home/pi/klipper_filament/venv/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import os
import configparser

CONFIG_FILE = 'config.ini'
NETWORK_TIMEOUT = 15 

def load_config():
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILE)
    
    if not os.path.exists(config_path):
        print(f"Error: Config '{config_path}' not found.")
        sys.exit(1)
        
    config.read(config_path)
    try:
        spoolman_url = config['Spoolman']['SPOOLMAN_URL']
        moonraker_base_url = config['Moonraker']['MOONRAKER_URL'] 
        if not moonraker_base_url.endswith('/'):
            moonraker_base_url += '/'
        return spoolman_url, moonraker_base_url
    except KeyError as e:
        print(f"Config Error: Missing {e}.")
        sys.exit(1)

def get_filament_data(filament_id, spoolman_url):
    # Si el ID es 0, no consultamos Spoolman (ahorramos tiempo en errores de inicio)
    if str(filament_id) == "0":
        return "Cualquiera", "Cualquiera"
        
    try:
        url = f"{spoolman_url}{filament_id}" 
        resp = requests.get(url, timeout=NETWORK_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("name", "Unknown"), data.get("material", "Unknown")
    except requests.exceptions.RequestException as e:
        print(f"Error Spoolman {filament_id}: {e}")
        return "Unknown", "Unknown"

def send_filament_info(fid, name, material, motivo, moonraker_base_url):
    MOONRAKER_GCODE_URL = f"{moonraker_base_url}printer/gcode/script"
    
    safe_name = str(name).replace('"', "'")
    safe_material = str(material).replace('"', "'")
    safe_motivo = str(motivo).replace('"', "'")

    # Enviamos el comando incluyendo el MOTIVO
    gcode = f'_FILAMENT_INFO ID={fid} NAME="{safe_name}" MATERIAL="{safe_material}" MOTIVO="{safe_motivo}"'

    try:
        requests.post(MOONRAKER_GCODE_URL, json={"script": gcode}, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Moonraker POST failed: {e}")

def main():
    SPOOLMAN_URL, MOONRAKER_BASE_URL = load_config()

    # Ahora esperamos 2 argumentos: ID y MOTIVO
    if len(sys.argv) < 3:
        print("Uso: filamentNotice.py <filament_id> <motivo>")
        sys.exit(1)

    filament_id = sys.argv[1]
    motivo = sys.argv[2]
    
    name, material = get_filament_data(filament_id, SPOOLMAN_URL)
    send_filament_info(filament_id, name, material, motivo, MOONRAKER_BASE_URL)

    print(f"FILAMENT_NOTICE finished for {motivo}")
    sys.exit(0) 

if __name__ == "__main__":
    main()
