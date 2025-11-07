#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import sys
import re
import requests
import os

# URL base del servidor Spoolman
SPOOLMAN_URL = "http://192.168.0.220:7912/api/v1/filament/"

# Carpeta donde Klipper guarda los G-code
GCODE_PATH = "/home/pi/printer_data/gcodes/"

def get_filament_info(filament_id):
    """Consulta la API de Spoolman y devuelve nombre y material."""
    try:
        response = requests.get(f"{SPOOLMAN_URL}{filament_id}", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return {
                "id": filament_id,
                "name": data.get("name", "Unknown"),
                "material": data.get("material", "Unknown")
            }
        else:
            return {"id": filament_id, "name": "Unknown", "material": "Unknown"}
    except Exception as e:
        return {"id": filament_id, "name": "Error", "material": str(e)}

def parse_gcode(filepath):
    """
    Busca todas las líneas con ASSERT_ACTIVE_FILAMENT ID=x
    Devuelve la lista en orden de aparición.
    """
    cambios = []
    try:
        with open(filepath, "r", encoding="utf-8", errors="ignore") as f:
            for linea in f:
                linea = linea.strip()
                match_fil = re.search(r"ASSERT_ACTIVE_FILAMENT\s+ID=(\d+)", linea)
                if match_fil:
                    fid = int(match_fil.group(1))
                    cambios.append(fid)
    except FileNotFoundError:
        print(f"Error: archivo no encontrado -> {filepath}")
        sys.exit(1)
    return cambios

def main():
    if len(sys.argv) < 2:
        print("Uso: FilamentList.py <archivo.gcode>")
        sys.exit(1)

    filename = sys.argv[1]
    if not os.path.isabs(filename):
        filename = os.path.join(GCODE_PATH, filename)

    cambios = parse_gcode(filename)
    if not cambios:
        print("No se encontraron cambios de filamento.")
        sys.exit(0)

    print("Secuencia de filamentos detectada:")
    for i, fid in enumerate(cambios, start=1):
        info = get_filament_info(fid)
        print(f"  Cambio {i}: ID={fid} | Nombre={info['name']} | Material={info['material']}")

    print("\nAnálisis completado correctamente.")

if __name__ == "__main__":
    main()
