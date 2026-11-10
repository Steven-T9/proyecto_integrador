"""Rol C: lectores de archivos. Implementación del estudiante en semana 12.

Contrato de salida para cada lector: list[dict] con claves id, tipo, valor, unidad.
Los lectores no normalizan ni clasifican: entregan datos crudos al servicio.
"""
import csv
import json
from pathlib import Path


def leer_csv(archivo):
    # TODO C-S12-01: leer CSV y devolver lista de diccionarios.
    # raise NotImplementedError("Pendiente: lector CSV, semana 12")

    registros = []
    ruta = Path(archivo)
    
    # Manejo de archivos inexistentes o vacíos
    if not ruta.exists() or ruta.stat().st_size == 0:
        return []
        
    try:
        with open(ruta, mode='r', encoding='utf-8') as f:
            lector = csv.DictReader(f)
            for fila in lector:
                registros.append(dict(fila))
    except Exception:
        return []
        
    return registros

def leer_json(archivo):
    # TODO C-S12-02: leer JSON y devolver lista de diccionarios.
    # raise NotImplementedError("Pendiente: lector JSON, semana 12")
    ruta = Path(archivo)

    if not ruta.exists() or ruta.stat().st_size == 0:
        return []
        
    try:
        with open(ruta, mode='r', encoding='utf-8') as f:
            datos = json.load(f)
            if isinstance(datos, list):
                return datos
            elif isinstance(datos, dict):
                # Soporte por si el JSON viene encapsulado en una clave contenedora
                return datos.get("registros", [datos])
            return []
    except (json.JSONDecodeError, Exception):
        return []
    # Manejo de archivos inexistentes o vacíos
def leer_excel(archivo):
    # TODO C-S12-03: leer Excel y devolver lista de diccionarios.
    # raise NotImplementedError("Pendiente: lector Excel, semana 12")
    ruta = Path(archivo)
    
    
    if not ruta.exists():
      return []
        
    try:
        # Usamos pandas para leer la primera hoja del archivo Excel
        df = pd.read_excel(ruta)
        if df.empty:
            return []
        # Convierte el DataFrame de pandas directamente a una lista de diccionarios
        return df.to_dict(orient="records")
    except Exception:
        return []
