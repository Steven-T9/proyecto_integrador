"""Rol C: adaptador de fuentes en memoria."""
from src.data.sensores import obtener_registros

def cargar_desde_memoria():
    """Fuente de datos funcional desde la primera entrega."""
    return obtener_registros()

def preparar_registros_prueba():
    """Rol C: escenarios adicionales de entrada para pruebas de semana 10."""
    # TODO C-S10-01: construir registros con espacios, mayúsculas y formatos diversos.
    # TODO C-S10-02: construir casos incompletos y tipos no reconocidos.
    # TODO C-S10-03: no alterar los 12 registros base.
    raise NotImplementedError("Pendiente: implementación del rol C, semana 10")


    """
Rol C: Adaptador de fuentes en memoria.
Proyecto DataLab - Semana 10
Responsable de proveer los datos base y escenarios de prueba con anomalías
para evaluar la normalización (Rol A) y la robustez (Rol B).
"""


def cargar_desde_memoria():
    """
    Fuente de datos funcional desde la primera entrega.
    Retorna los 12 registros limpios y base originales.
    """
    return obtener_registros()

def preparar_registros_prueba():
    """
    Rol C: Escenarios adicionales de entrada para pruebas de semana 10.
    
    Introduce a propósito "trampas" y datos sucios (espacios, mayúsculas, 
    formatos diversos, datos incompletos y tipos no reconocidos) para 
    poner a prueba los módulos de Calidad (Rol A) y Robustez (Rol B).
    """
    # TODO C-S10-03: No alterar los 12 registros base originales.
    # Usamos copy.deepcopy para garantizar que la fuente original no sufra modificaciones.
    registros_base = obtener_registros()
    registros_copia = copy.deepcopy(registros_base)
    
    # TODO C-S10-01 y C-S10-02: Escenarios de prueba con anomalías intencionales.
    registros_prueba_extra = [
        {
            # Caso 1: Espacios sobrantes y mayúsculas (Prueba de normalización del Rol A)
            "id": "   sens_013_espacios   ",
            "valor": " 24.5 °C ",
            "tipo": "TEMPERATURA",  # En mayúsculas a propósito
            "unidad": "celsius",
            "timestamp": "2026-11-05 09:00:00"
        },
        {
            # Caso 2: Tipo de valor no numérico (Prueba de manejo de excepciones del Rol B)
            "id": "SENS-014",
            "valor": "VALOR_NO_NUMERICO",  
            "tipo": "humedad",
            "unidad": "%",
            "timestamp": "2026-11-05 09:01:00"
        },
        {
            # Caso 3: Registro incompleto (Faltan claves obligatorias como unidad y timestamp)
            "id": "SENS-015",
            "valor": 1013.25,
            "tipo": "presion"
        },
        {
            # Caso 4: Tipo de sensor desconocido y formato de fecha atípico
            "id": "SENS-016",
            "valor": 55.0,
            "tipo": "TIPO_DESCONOCIDO_XYZ",
            "unidad": "desconocida",
            "timestamp": "ayer por la tarde"
        }
    ]
    
    # Retornamos la combinación de la copia intacta de los 12 base + las 4 pruebas sucias
    return registros_copia + registros_prueba_extra



import os

# Creamos la estructura de carpetas interna en Colab
os.makedirs("src/data", exist_ok=True)
os.makedirs("tests", exist_ok=True)

print("¡Estructura de carpetas creada con éxito!")

def obtener_registros():
    """Simula los 12 registros base originales de la primera entrega."""
    return [
        {"id": f"sens_{i:03d}", "valor": 20.0 + i, "tipo": "temperatura", "unidad": "celsius", "timestamp": "2026-11-05 08:00:00"}
        for i in range(1, 13)
    ]


"""
Rol C: Adaptador de fuentes en memoria.
Proyecto DataLab - Semana 10
"""

import copy
from src.data.sensores import obtener_registros

def cargar_desde_memoria():
    """Fuente de datos funcional desde la primera entrega."""
    return obtener_registros()

def preparar_registros_prueba():
    """Rol C: escenarios adicionales de entrada para pruebas de semana 10."""
    registros_base = obtener_registros()
    registros_copia = copy.deepcopy(registros_base)
    
    registros_prueba_extra = [
        {
            "id": "   sens_013_espacios   ",
            "valor": " 24.5 °C ",
            "tipo": "TEMPERATURA",  
            "unidad": "celsius",
            "timestamp": "2026-11-05 09:00:00"
        },
        {
            "id": "SENS-014",
            "valor": "VALOR_NO_NUMERICO",  
            "tipo": "humedad",
            "unidad": "%",
            "timestamp": "2026-11-05 09:01:00"
        },
        {
            "id": "SENS-015",
            "valor": "1013.25",
            "tipo": "presion"
        },
        {
            "id": "SENS-016",
            "valor": "55.0",
            "tipo": "TIPO_DESCONOCIDO_XYZ",
            "unidad": "desconocida",
            "timestamp": "ayer por la tarde"
        }
    ]
    
    return registros_copia + registros_prueba_extra