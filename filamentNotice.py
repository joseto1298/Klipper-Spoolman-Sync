#!/home/pi/Klipper-Spoolman-Sync/venv/bin/python3
# -*- coding: utf-8 -*-

"""
Script: filamentNotice.py
Función: Consulta Spoolman para obtener información de un filamento y
         envía esta información como un comando G-code a Klipper a través de Moonraker.
Incluye caché local para evitar consultas repetidas a Spoolman.
"""

import sys
import requests
import os
import configparser
import json

# --- CONFIGURACIÓN Y CARGA ---
CONFIG_FILE = 'config.ini'
NETWORK_TIMEOUT = 15
CACHE_FILE = 'filament_cache.json'

def load_config():
    config = configparser.ConfigParser()
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILE)
    
    if not os.path.exists(config_path):
        print(f"Error: El archivo de configuración '{config_path}' no se encontró.")
        sys.exit(1)
        
    config.read(config_path)
    
    try:
        spoolman_url = config['Spoolman']['SPOOLMAN_URL']
        moonraker_base_url = config['Moonraker']['MOONRAKER_URL']
        
        if not moonraker_base_url.endswith('/'):
            moonraker_base_url += '/'
            
        return spoolman_url, moonraker_base_url
        
    except KeyError as e:
        print(f"Error en el archivo de configuración: Falta la clave o sección {e}.")
        sys.exit(1)


def get_cache_path():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, CACHE_FILE)


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


def get_filament_data(filament_id, spoolman_url):
    cache = load_cache()
    str_id = str(filament_id)

    if str_id in cache:
        data = cache[str_id]
        return data.get("name", "Unknown"), data.get("material", "Unknown"), data.get("vendor", "Unknown")

    try:
        url = f"{spoolman_url}{filament_id}"
        resp = requests.get(url, timeout=NETWORK_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
        
        name = data.get("name", "Unknown")
        material = data.get("material", "Unknown")
        vendor_name = data.get("vendor", {}).get("name", "Unknown")

        cache[str_id] = {"name": name, "material": material, "vendor": vendor_name}
        save_cache(cache)
        
        return name, material, vendor_name
        
    except requests.exceptions.RequestException as e:
        print(f"Error al obtener filamento {filament_id} de Spoolman: {e}")
        return "Unknown", "Unknown", "Unknown"


def send_filament_info(fid, name, material, vendor_name, moonraker_base_url):
    MOONRAKER_GCODE_URL = f"{moonraker_base_url}printer/gcode/script"

    safe_name = str(name).replace('"', "'")
    safe_material = str(material).replace('"', "'")
    safe_vendor = str(vendor_name).replace('"', "'")

    gcode = f'_FILAMENT_INFO ID={fid} NAME="{safe_name}" MATERIAL="{safe_material}" VENDOR="{safe_vendor}"'

    try:
        requests.post(
            MOONRAKER_GCODE_URL,
            json={"script": gcode},
        )
        print(f"SUCCESS: Datos del filamento enviados a Klipper correctamente.")
    except requests.exceptions.RequestException as e:
        print(f"Moonraker POST failed: {e}")

def main():
    SPOOLMAN_URL, MOONRAKER_BASE_URL = load_config()

    if len(sys.argv) < 2:
        print("Uso: filamentNotice.py <filament_id>")
        sys.exit(1)

    filament_id = sys.argv[1]
    
    name, material, vendor_name = get_filament_data(filament_id, SPOOLMAN_URL)
    send_filament_info(filament_id, name, material, vendor_name, MOONRAKER_BASE_URL)

    print("FILAMENT_NOTICE finished")
    sys.exit(0) 


if __name__ == "__main__":
    main()
