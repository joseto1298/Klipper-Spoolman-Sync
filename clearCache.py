#!/home/pi/Klipper-Spoolman-Sync/venv/bin/python3
# -*- coding: utf-8 -*-

"""
Script: clearCache.py
Función: Elimina el archivo de caché de filamentos.
"""

import os
import sys

CACHE_FILE = 'filament_cache.json'

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    cache_path = os.path.join(script_dir, CACHE_FILE)

    if os.path.exists(cache_path):
        os.remove(cache_path)
        print("✅ Caché de filamentos eliminada correctamente.")
    else:
        print("ℹ️ No existía ningún archivo de caché.")

if __name__ == "__main__":
    main()
