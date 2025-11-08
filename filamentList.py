#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Script: filamentList.py
# Propósito: Lee la configuración de 'config.ini' y sincroniza el uso de filamento
# en Klipper/Moonraker con la base de datos de Spoolman.

import sys
import re
import requests
import os
import configparser

# --- CONFIGURACIÓN DE ARCHIVOS ---

# Obtiene la ruta absoluta del directorio donde se está ejecutando este script.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Construye la ruta completa al archivo config.ini
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.ini")

# --- CARGA DE CONFIGURACIÓN ---

def load_config():
    """Carga y valida los parámetros de configuración desde config.ini."""
    config = configparser.ConfigParser()
    
    # Usa la ruta absoluta construida arriba (CONFIG_FILE)
    if not os.path.exists(CONFIG_FILE):
        # Si no lo encuentra, imprime la ruta que intentó usar
        print(f"Error: Archivo de configuración '{CONFIG_FILE}' no encontrado.")
        sys.exit(1)
        
    config.read(CONFIG_FILE)
    
    settings = {}
    try:
        settings["SPOOLMAN_URL"] = config.get("Spoolman", "SPOOLMAN_URL")
        settings["GCODE_PATH"] = config.get("Klipper", "GCODE_PATH")
        # settings["MOONRAKER_URL"] = config.get("Moonraker", "MOONRAKER_URL") 
    except configparser.NoSectionError as e:
        print(f"Error en config.ini: Falta una sección o clave requerida: {e}")
        sys.exit(1)
    
    return settings

# Carga la configuración al inicio del script
CONFIG = load_config()
SPOOLMAN_URL = CONFIG["SPOOLMAN_URL"]
GCODE_PATH = CONFIG["GCODE_PATH"]

# --- FUNCIONES PRINCIPALES ---

def get_filament_info(filament_id):
    """
    Consulta la API de Spoolman para obtener detalles de un filamento específico.
    """
    try:
        # Usa la URL cargada desde config.ini
        response = requests.get(f"{SPOOLMAN_URL}{filament_id}", timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                "id": filament_id,
                "name": data.get("name", "Unknown"),
                "material": data.get("material", "Unknown")
            }
        else:
            return {"id": filament_id, "name": "ID No Encontrado", "material": "Desconocido"}
    
    except requests.exceptions.RequestException as e:
        return {"id": filament_id, "name": "Error de Conexión", "material": str(e)}

def parse_gcode(filepath):
    """
    Lee un archivo G-code, busca IDs de filamento (ASSERT_ACTIVE_FILAMENT ID=x)
    y elimina IDs consecutivos iguales.
    """
    
    all_fids = []
    
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                linea = linea.strip()
                match_fil = re.search(r"ASSERT_ACTIVE_FILAMENT\s+ID=(\d+)", linea)
                
                if match_fil:
                    fid = int(match_fil.group(1))
                    all_fids.append(fid)

    except FileNotFoundError:
        print(f"Error: archivo G-code no encontrado -> {filepath}")
        sys.exit(1)
        
    # --- Lógica de Desduplicación Consecutiva ---
    unique_sequence = []
    last_fid = None
    
    for fid in all_fids:
        if fid != last_fid:
            unique_sequence.append(fid)
            last_fid = fid
            
    return unique_sequence

# --- FUNCIÓN DE EJECUCIÓN PRINCIPAL ---

def main():
    """
    Función principal que gestiona la entrada de argumentos y coordina el análisis.
    """
    
    if len(sys.argv) < 2:
        print("Uso: filamentList.py <archivo.gcode>")
        sys.exit(1)

    filename = sys.argv[1]
    
    # Usa GCODE_PATH cargada desde config.ini
    if not os.path.isabs(filename):
        filename = os.path.join(GCODE_PATH, filename)

    cambios = parse_gcode(filename)
    
    if not cambios:
        print("No se encontraron comandos ASSERT_ACTIVE_FILAMENT ni cambios de filamento.")
        sys.exit(0)

    print("Secuencia de filamentos detectada:")
    print("-" * 35)
    
    for i, fid in enumerate(cambios, start=1):
        info = get_filament_info(fid)
        print(f"  Cambio {i}: ID={fid} | Nombre={info['name']} | Material={info['material']}")

    print("\nAnálisis completado correctamente.")

if __name__ == "__main__":
    main()