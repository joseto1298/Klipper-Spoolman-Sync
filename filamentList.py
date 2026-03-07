#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import re
import requests
import os
import configparser

# --- CARGA DE CONFIGURACIÓN ---
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = os.path.join(SCRIPT_DIR, "config.ini")

def load_config():
    """Lee config.ini y normaliza las URLs y rutas."""
    config = configparser.ConfigParser()
    if not os.path.exists(CONFIG_FILE):
        print(f"Error: No se encontró '{CONFIG_FILE}'")
        sys.exit(1)
        
    config.read(CONFIG_FILE)
    try:
        # Normalizamos URLs y rutas para que siempre terminen en /
        spool_url = config.get("Spoolman", "SPOOLMAN_URL").rstrip('/') + '/'
        gcode_path = config.get("Klipper", "GCODE_PATH").rstrip('/') + '/'
        return spool_url, gcode_path
    except Exception as e:
        print(f"Error en las claves de config.ini: {e}")
        sys.exit(1)

# Variables globales de configuración
SPOOLMAN_URL, GCODE_PATH = load_config()

def get_filament_info(filament_id):
    """Consulta detalles del filamento en Spoolman."""
    try:
        url = f"{SPOOLMAN_URL}{filament_id}"
        # Si por alguna razón la URL no tiene la palabra filament, la añadimos
        if "/filament/" not in url:
            url = f"{SPOOLMAN_URL}filament/{filament_id}"
            
        response = requests.get(url, timeout=5)
        if response.status_code == 200:
            data = response.json()
            vendor = data.get("vendor", {}).get("name", "")
            name = data.get("name", "Desconocido")
            mat = data.get("material", "N/A")
            
            full_name = f"{vendor} {name}".strip()
            return {"name": full_name, "material": mat}
        return {"name": f"ID {filament_id} no encontrado", "material": "?"}
    except:
        return {"name": "Error de conexión", "material": "Error"}

def parse_gcode(filepath):
    """Escanea el archivo buscando comandos ASSERT_ACTIVE_FILAMENT."""
    # Validación crucial para evitar el Errno 21 (IsADirectoryError)
    if os.path.isdir(filepath):
        print(f"ERROR: '{filepath}' es una carpeta, no un archivo G-code.")
        return []

    fids = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for line in f:
                # Buscamos la etiqueta de filamento
                match = re.search(r"ASSERT_ACTIVE_FILAMENT\s+ID=(\d+)", line)
                if match:
                    fids.append(int(match.group(1)))
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return []

    # Eliminar duplicados consecutivos (1, 1, 2 -> 1, 2)
    secuencia_unica = []
    ultimo_id = None
    for fid in fids:
        if fid != ultimo_id:
            secuencia_unica.append(fid)
            ultimo_id = fid
    return secuencia_unica

def main():
    if len(sys.argv) < 2:
        print("Uso: filamentList.py <nombre_archivo_o_ruta>")
        sys.exit(1)

    # Capturamos el argumento de Klipper (limpiamos comillas si las hay)
    entrada = sys.argv[1].strip().replace('"', '').replace("'", "")

    # LÓGICA DE RUTA INTELIGENTE:
    # Si la entrada ya es una ruta absoluta (empieza por /), la usamos.
    # Si no, la concatenamos con el GCODE_PATH del config.ini.
    if os.path.isabs(entrada):
        filepath = entrada
    else:
        filepath = os.path.join(GCODE_PATH, entrada)

    print(f"\n📂 Archivo: {os.path.basename(filepath)}")
    print(f"📍 Ruta: {filepath}")
    
    secuencia = parse_gcode(filepath)
    
    if not secuencia:
        print("ℹ️  No se detectaron comandos de filamento en este archivo.")
        return

    print("\n🧵 SECUENCIA DE FILAMENTOS DETECTADA")
    print("=" * 50)
    for i, fid in enumerate(secuencia, start=1):
        info = get_filament_info(fid)
        print(f" {i}. [ID {fid:3}] -> {info['name']} ({info['material']})")
    print("=" * 50)
    print("✅ Análisis finalizado.\n")

if __name__ == "__main__":
    main()
