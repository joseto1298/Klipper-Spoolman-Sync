#!/home/pi/klipper_filament/venv/bin/python3
# -*- coding: utf-8 -*-

import sys
import requests
import os
import configparser
import time

CONFIG_FILE = 'config.ini'
NETWORK_TIMEOUT = 5

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

# NUEVA FUNCIÓN: Notificación rápida a la pantalla
def send_status_update(message, moonraker_base_url):
    url = f"{moonraker_base_url}printer/gcode/script"
    try:
        # Usamos M117 porque es instantáneo en pantallas BTT
        requests.post(url, json={"script": f'M117 {message}'}, out=1)
    except:
        pass

def get_filament_data(filament_id, spoolman_url):
    if str(filament_id) == "0":
        return "Cualquiera", "Cualquiera"
        
    try:
        # Aseguramos que la URL de Spoolman termine en / para la API
        base_url = spoolman_url if spoolman_url.endswith('/') else f"{spoolman_url}/"
        url = f"{base_url}filament/{filament_id}" # Ajustado a la ruta estándar de Spoolman
        
        resp = requests.get(url, out=NETWORK_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        return data.get("name", "Unknown"), data.get("material", "Unknown")
    except Exception as e:
        print(f"Error Spoolman {filament_id}: {e}")
        return "Unknown", "Unknown"

def send_filament_info(fid, name, material, motivo, moonraker_base_url):
    MOONRAKER_GCODE_URL = f"{moonraker_base_url}printer/gcode/script"
    
    safe_name = str(name).replace('"', "'")
    safe_material = str(material).replace('"', "'")
    
    # Preparamos el comando final
    gcode = f'_FILAMENT_INFO ID={fid} NAME="{safe_name}" MATERIAL="{safe_material}" MOTIVO="{motivo}"'

    try:
        time.sleep(0.3) 
        requests.post(MOONRAKER_GCODE_URL, json={"script": gcode}, timeout=5)
    except requests.exceptions.RequestException as e:
        print(f"Moonraker POST failed: {e}")

def main():
    SPOOLMAN_URL, MOONRAKER_BASE_URL = load_config()

    if len(sys.argv) < 3:
        sys.exit(1)

    filament_id = sys.argv[1]
    motivo = sys.argv[2]
    
    # 1. Feedback inmediato al lanzar el script
    send_status_update("Consultando Spoolman...", MOONRAKER_BASE_URL)
    
    # 2. Obtenemos datos (Aquí está el retardo de red)
    name, material = get_filament_data(filament_id, SPOOLMAN_URL)
    
    # 3. Informamos que ya tenemos los datos
    send_status_update("Abriendo menú...", MOONRAKER_BASE_URL)
    
    # 4. Enviamos el macro final que abre el prompt
    send_filament_info(filament_id, name, material, motivo, MOONRAKER_BASE_URL)

    sys.exit(0) 

if __name__ == "__main__":
    main()
