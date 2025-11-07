#!/home/pi/klipper_filament/venv/bin/python3
# -*- coding: utf-8 -*-

"""
Script: filamentNotice.py
Function: Queries Spoolman for filament information and notifies Klipper.
"""

import sys
import requests
import os
import configparser

# --- CONFIGURACIÓN Y CARGA ---
CONFIG_FILE = 'config.ini'

def load_config():
    """Carga las configuraciones necesarias desde config.ini."""
    config = configparser.ConfigParser()
    
    # Intenta buscar config.ini en la ruta actual o en el directorio del script
    if not os.path.exists(CONFIG_FILE):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(script_dir, CONFIG_FILE)
        
        if not os.path.exists(config_path):
            print(f"Error: El archivo de configuración '{CONFIG_FILE}' no se encontró.")
            sys.exit(1)
        
        config.read(config_path)
    else:
        config.read(CONFIG_FILE)
    
    try:
        spoolman_url = config['Spoolman']['SPOOLMAN_URL']
        moonraker_base_url = config['Moonraker']['MOONRAKER_BASE_URL']
        
        # Asegurar que la URL base de Moonraker termina en /
        if not moonraker_base_url.endswith('/'):
            moonraker_base_url += '/'
            
        return spoolman_url, moonraker_base_url
        
    except KeyError as e:
        print(f"Error en el archivo de configuración: Falta la clave o sección {e}.")
        sys.exit(1)


def get_filament_data(filament_id, spoolman_url):
    """Fetch name and material from Spoolman using the configured URL."""
    try:
        # Nota: La URL de Spoolman en el config.ini no debe terminar en /filament/
        url = f"{spoolman_url}/{filament_id}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        data = resp.json()
        name = data.get("name", "Unknown")
        material = data.get("material", "Unknown")
        return name, material
    except requests.exceptions.RequestException as e:
        print(f"Error fetching filament {filament_id} from Spoolman: {e}")
        return "Unknown", "Unknown"


def send_filament_info(fid, name, material, moonraker_base_url):
    """Send FILAMENT_INFO command to Klipper through Moonraker."""
    
    # Construir el endpoint completo para enviar comandos G-code
    MOONRAKER_GCODE_URL = f"{moonraker_base_url}printer/gcode/script"
    
    safe_name = str(name).replace('"', "'")
    safe_material = str(material).replace('"', "'")
    gcode = f'FILAMENT_INFO ID={fid} NAME="{safe_name}" MATERIAL="{safe_material}"'

    try:
        r = requests.post(MOONRAKER_GCODE_URL, json={"script": gcode}, timeout=5)
        r.raise_for_status()
        print(f"Sent to Klipper: {gcode}")
    except requests.exceptions.RequestException as e:
        print(f"Error sending to Klipper at {MOONRAKER_GCODE_URL}: {e}")


def main():
    # 1. Cargar las configuraciones
    SPOOLMAN_URL, MOONRAKER_BASE_URL = load_config()

    if len(sys.argv) < 2:
        print("Usage: filamentNotice.py <filament_id>")
        sys.exit(1)

    filament_id = sys.argv[1]
    print(f"Querying filament ID={filament_id} from Spoolman...")

    # 2. Pasar SPOOLMAN_URL a la función
    name, material = get_filament_data(filament_id, SPOOLMAN_URL)
    print(f"Filament: {name} ({material})")

    # 3. Pasar MOONRAKER_BASE_URL a la función
    send_filament_info(filament_id, name, material, MOONRAKER_BASE_URL)


if __name__ == "__main__":
    main()