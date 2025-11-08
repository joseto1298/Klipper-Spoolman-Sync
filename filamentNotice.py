#!/home/pi/klipper_filament/venv/bin/python3
# -*- coding: utf-8 -*-

"""
Script: filamentNotice.py
Función: Consulta Spoolman para obtener información de un filamento y
         envía esta información como un comando G-code a Klipper a través de Moonraker.
"""

import sys
import requests
import os
import configparser

# --- CONFIGURACIÓN Y CARGA ---
# Nombre del archivo de configuración.
CONFIG_FILE = 'config.ini'
# Tiempo de espera máximo para las peticiones de red (ajustado para mayor fiabilidad).
NETWORK_TIMEOUT = 15 

def load_config():
    """
    Carga y valida las configuraciones necesarias desde config.ini.
    Busca config.ini en el directorio donde reside el script.
    """
    config = configparser.ConfigParser()
    
    # 1. Determinar la ruta absoluta del archivo de configuración
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_path = os.path.join(script_dir, CONFIG_FILE)
    
    # 2. Verificar existencia y leer
    if not os.path.exists(config_path):
        print(f"Error: El archivo de configuración '{config_path}' no se encontró.")
        sys.exit(1) # CRÍTICO: Sale con error si el archivo no existe.
        
    config.read(config_path)
    
    try:
        # Extrae las URLs necesarias
        spoolman_url = config['Spoolman']['SPOOLMAN_URL']
        # Corregido: Uso de MOONRAKER_URL tal como está en el .ini
        moonraker_base_url = config['Moonraker']['MOONRAKER_URL'] 
        
        # Asegurar que la URL base de Moonraker termina en /
        if not moonraker_base_url.endswith('/'):
            moonraker_base_url += '/'
            
        return spoolman_url, moonraker_base_url
        
    except KeyError as e:
        print(f"Error en el archivo de configuración: Falta la clave o sección {e}.")
        sys.exit(1) # CRÍTICO: Sale con error si la configuración es incorrecta.


def get_filament_data(filament_id, spoolman_url):
    """
    Obtiene el nombre y material de un filamento desde Spoolman.
    """
    try:
        # La URL de Spoolman debería tener el formato base (ej. http://ip:port/api/v1/filament)
        url = f"{spoolman_url}{filament_id}" 
        # Aumentamos el timeout para evitar fallos por red lenta.
        resp = requests.get(url, timeout=NETWORK_TIMEOUT)
        resp.raise_for_status() # Lanza un error si el código HTTP es 4xx o 5xx.
        data = resp.json()
        
        name = data.get("name", "Unknown")
        material = data.get("material", "Unknown")
        return name, material
        
    except requests.exceptions.RequestException as e:
        # Si la consulta falla, imprime el error y devuelve valores por defecto, 
        # pero permite continuar a Moonraker para que el error sea manejado por Klipper.
        print(f"Error al obtener filamento {filament_id} de Spoolman: {e}")
        return "Unknown", "Unknown"


def send_filament_info(fid, name, material, moonraker_base_url):
    """
    Envía el comando FILAMENT_INFO a Klipper a través del endpoint de G-code de Moonraker.
    """
    
    MOONRAKER_GCODE_URL = f"{moonraker_base_url}printer/gcode/script"
    
    safe_name = str(name).replace('"', "'")
    safe_material = str(material).replace('"', "'")
    
    # CRÍTICO: Usar un macro con '_' (ej. _FILAMENT_INFO) para macros internos.
    gcode = f'_FILAMENT_INFO ID={fid} NAME="{safe_name}" MATERIAL="{safe_material}"'

    # Se envía el comando.
    requests.post(MOONRAKER_GCODE_URL, json={"script": gcode})

def main():
    # 1. Cargar las configuraciones
    SPOOLMAN_URL, MOONRAKER_BASE_URL = load_config()

    if len(sys.argv) < 2:
        print("Uso: filamentNotice.py <filament_id>")
        sys.exit(1)

    filament_id = sys.argv[1]
    
    # 2. Obtener la información del filamento
    name, material = get_filament_data(filament_id, SPOOLMAN_URL)

    # 3. Enviar la información a Klipper
    send_filament_info(filament_id, name, material, MOONRAKER_BASE_URL)

    # Si llega hasta aquí, el script ha terminado con éxito.
    sys.exit(0) 


if __name__ == "__main__":
    main()