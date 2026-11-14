"""Rol C: adaptador de fuentes en memoria y escenarios de prueba.

Una "fuente" es cualquier lugar del que salen registros. En memoria no hay
archivos: los registros se construyen en Python. Sirven para la demostración y
para probar los módulos de los roles A y B con casos controlados.

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
import copy

from src.data.sensores import obtener_registros

# REVISIÓN (C-4): el archivo tenía TRES versiones de las mismas funciones y,
# entre ellas, código de Google Colab:
#     os.makedirs("src/data", exist_ok=True)
#     os.makedirs("tests", exist_ok=True)
#     print("¡Estructura de carpetas creada con éxito!")
# Todo lo que está en el nivel superior de un módulo se ejecuta al importarlo,
# así que cada import (Streamlit, consola, pruebas) creaba carpetas en el
# directorio actual. También se redefinía obtener_registros() con otros datos
# (sens_001...); solo funcionaba porque el último bloque volvía a importar la
# original, es decir, el resultado dependía del ORDEN del código.
# Nunca se redefinen funciones de otro módulo; para guardar versiones
# anteriores está Git.


def cargar_desde_memoria():
    """Fuente de datos funcional desde la primera entrega (12 registros base)."""
    # REVISIÓN (C-4): se devuelve una copia profunda. Si alguien modifica la
    # lista recibida, los datos base de sensores.py no cambian (C-S10-03).
    return copy.deepcopy(obtener_registros())


def preparar_registros_prueba():
    """Semana 10: registros base + casos con formatos diversos.

    Resultado esperado al procesarlos (para las pruebas del equipo):
    - Los 12 registros base son válidos.
    - T-ESP, H-COMA y P-TILDE son válidos tras la normalización.
    - Los demás son inválidos y cada uno indica sus motivos.
    """
    # C-S10-03: no alterar los 12 registros base -> se trabaja sobre una copia.
    registros = cargar_desde_memoria()

    # C-S10-01: espacios, mayúsculas, tildes y formatos diversos.
    # Se conservan los escenarios del equipo (espacios, mayúsculas, valor con
    # unidad incluida, no numérico, incompleto, tipo desconocido).
    # REVISIÓN (C-4): se agregan casos para comprobar las normalizaciones del
    # Rol A (coma decimal, tilde en el tipo, unidad en mayúsculas).
    registros += [
        {"id": "  T-ESP  ", "tipo": "  TEMPERATURA ", "valor": " 24.5 ", "unidad": " celsius "},
        {"id": "H-COMA", "tipo": "Humedad", "valor": "55,2", "unidad": "%"},
        {"id": "P-TILDE", "tipo": "Presión", "valor": "1013.2", "unidad": "HPA"},
        {"id": "T-UNIDAD-EN-VALOR", "tipo": "temperatura", "valor": "24.5 °C", "unidad": "°C"},
    ]

    # C-S10-02: casos incompletos y tipos no reconocidos.
    registros += [
        {"id": "H-NO-NUM", "tipo": "humedad", "valor": "VALOR_NO_NUMERICO", "unidad": "%"},
        {"id": "P-SIN-UNIDAD", "tipo": "presion", "valor": "1013.25"},
        {"id": "X-TIPO", "tipo": "viento", "valor": "55.0", "unidad": "km/h"},
        {"id": "", "tipo": "temperatura", "valor": None, "unidad": "°F"},
    ]
    return registros


# REVISIÓN (C-7): función nueva. La semana 11 pide al Rol C "escenarios de
# fuentes defectuosas" y no existían. No hay que confundirlos con los datos de
# mala calidad de preparar_registros_prueba (los rechaza el Rol A): estos son
# fallas del ORIGEN, que el Rol B debe registrar sin detener el lote.
def preparar_escenarios_defectuosos():
    """Semana 11: entradas defectuosas para probar la robustez del Rol B.

    Ninguno de estos casos debe detener el lote: los válidos se procesan y los
    defectuosos quedan como inválidos o como errores técnicos.
    """
    registros = cargar_desde_memoria()[:3]
    registros += [
        "esto no es un diccionario",                    # error: ESTRUCTURA
        None,                                           # error: ESTRUCTURA
        {"id": "T-TIMEOUT", "tipo": "temperatura", "valor": 21.0, "unidad": "°C",
         "observacion_tecnica": "SIMULACION_TIMEOUT_SENSOR"},  # error: TIMEOUT_SENSOR
        {"id": "T-BOOL", "tipo": "temperatura", "valor": True, "unidad": "°C"},  # inválido
        {"id": "T-INF", "tipo": "temperatura", "valor": "inf", "unidad": "°C"},  # inválido
        {"id": "T-999", "tipo": "temperatura", "valor": 999, "unidad": "°C"},    # inválido: fuera de rango
        {},                                             # inválido: faltan todos los campos
    ]
    return registros
