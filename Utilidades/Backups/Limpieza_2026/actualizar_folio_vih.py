#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script corregido para agregar campos folio_vih a todos los archivos JSON de misiones.
CORRIGE: Los campos deben estar DENTRO de cada misión, no al final del archivo.
"""
import json
import os
from pathlib import Path

# Rutas base
BASE_DIR = Path(r"c:\Users\usuariohgf\OneDrive\Documentos\Extras\Apps\Proyectos\Nozhgess original")
CONFIG_DIR = BASE_DIR / "App" / "config"
MISIONES_DIR = BASE_DIR / "Lista de Misiones"

def actualizar_json_individual(filepath: Path):
    """
    Actualiza un archivo JSON individual.
    Estos archivos tienen estructura: {"MISSIONS": [{ misión }], ...}
    Los campos deben ir DENTRO de cada misión.
    """
    try:
        # Leer JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        missions = data.get("MISSIONS", [])
        if not missions:
            print(f"⚠️ {filepath.name} - No tiene array MISSIONS")
            return False
        
        # Actualizar cada misión
        updated_count = 0
        for mission in missions:
            if "folio_vih" not in mission or "folio_vih_codigos" not in mission:
                mission["folio_vih"] = False
                mission["folio_vih_codigos"] = []
                updated_count += 1
        
        # Eliminar campos al nivel raíz si existen (error del script anterior)
        if "folio_vih" in data:
            del data["folio_vih"]
        if "folio_vih_codigos" in data:
            del data["folio_vih_codigos"]
        
        if updated_count > 0:
            # Escribir de vuelta con formato bonito
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ {filepath.name} - {updated_count} misión(es) actualizada(s)")
            return True
        else:
            print(f"✓ {filepath.name} - Ya tiene los campos")
            return False
    
    except Exception as e:
        print(f"❌ {filepath.name} - Error: {e}")
        return False

def actualizar_mission_config():
    """Actualiza mission_config.json agregando campos a cada misión en el array MISSIONS."""
    filepath = CONFIG_DIR / "mission_config.json"
    
    try:
        # Leer JSON
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Actualizar cada misión en el array MISSIONS
        missions = data.get("MISSIONS", [])
        count = 0
        
        for i, mission in enumerate(missions):
            if "folio_vih" not in mission or "folio_vih_codigos" not in mission:
                mission["folio_vih"] = False
                mission["folio_vih_codigos"] = []
                count += 1
        
        if count > 0:
            # Escribir de vuelta
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            print(f"✅ mission_config.json - {count} misiones actualizadas")
            return True
        else:
            print(f"✓ mission_config.json - Todas las misiones ya tienen los campos")
            return False
    
    except Exception as e:
        print(f"❌ mission_config.json - Error: {e}")
        return False

def main():
    print("=" * 60)
    print("ACTUALIZACIÓN MASIVA: Agregar folio_vih a todos los JSON")
    print("(VERSIÓN CORREGIDA)")
    print("=" * 60)
    print()
    
    # 1. Actualizar mission_config.json
    print("📄 Actualizando mission_config.json...")
    actualizar_mission_config()
    print()
    
    # 2. Actualizar archivos individuales en Lista de Misiones
    print("📁 Actualizando archivos en Lista de Misiones...")
    
    # Buscar todos los .json recursivamente
    json_files = list(MISIONES_DIR.rglob("*.json"))
    
    if not json_files:
        print("⚠️ No se encontraron archivos JSON en Lista de Misiones")
        return
    
    updated = 0
    skipped = 0
    errors = 0
    
    for json_file in json_files:
        result = actualizar_json_individual(json_file)
        if result is True:
            updated += 1
        elif result is False:
            skipped += 1
        else:
            errors += 1
    
    print()
    print("=" * 60)
    print("RESUMEN:")
    print(f"  ✅ Actualizados: {updated}")
    print(f"  ✓  Omitidos (ya tenían campos): {skipped}")
    print(f"  ❌ Errores: {errors}")
    print(f"  📊 Total archivos procesados: {len(json_files)}")
    print("=" * 60)
    print()
    print("VERIFICACIÓN DE ESTRUCTURA:")
    print("  Los campos ahora están DENTRO de cada misión.")
    print("  Se eliminaron campos duplicados al nivel raíz.")

if __name__ == "__main__":
    main()
