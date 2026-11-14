"""Rol C: lectores de archivos CSV, JSON y Excel (semana 12).

Contrato de salida para cada lector: list[dict] con, al menos, las claves
id, tipo, valor y unidad. Además se agregan dos metadatos de trazabilidad:
    _origen : nombre del archivo
    _fila   : número de fila en el archivo (para encontrar el dato y corregirlo)

Responsabilidades (y lo que NO hace un lector):
- SÍ: leer el archivo, verificar su estructura y entregar una salida homogénea.
- NO: normalizar, validar ni clasificar. Los valores se entregan "crudos";
  eso corresponde a los roles A y B.

Manejo de errores:
- Si TODO el archivo es ilegible o su estructura global es incorrecta, se
  lanza una excepción (ErrorLecturaFuente / ErrorFormatoFuente): no se puede
  confiar en ninguna de sus filas.
- Si solo UNA fila está mal formada, no se detiene la lectura: la fila se
  marca con `_error_estructura` y procesamiento.py la reporta como error.

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
# REVISIÓN (C-3): todas las importaciones van AL INICIO del archivo (PEP 8).
# Antes leer_excel usaba `pd.read_excel` sin `import pandas as pd`: el NameError
# quedaba oculto por `except Exception: return []` y humedad.xlsx se leía como
# un archivo sin registros (0 de 573).
import csv
import io
import json
import math
from datetime import date, datetime
from pathlib import Path

from src.exceptions.errores import ErrorFormatoFuente, ErrorLecturaFuente

COLUMNAS_OBLIGATORIAS = ("id", "tipo", "valor", "unidad")


# --------------------------------------------------------------------------
# Utilidades compartidas por los tres lectores (evitan duplicar código)
# --------------------------------------------------------------------------
def _nombre_de(archivo):
    """Devuelve el nombre del archivo, sea una ruta o un archivo subido."""
    if isinstance(archivo, (str, Path)):
        return Path(archivo).name
    return getattr(archivo, "name", "archivo")


def _leer_bytes(archivo):
    """Obtiene el contenido binario desde una ruta o desde un objeto archivo."""
    # REVISIÓN (C-1): los lectores solo aceptaban rutas (Path(archivo)). El
    # servicio docente les pasa el archivo que entrega st.file_uploader, que es
    # un objeto con .read() y no una ruta, así que los TRES datasets fallaban
    # con TypeError desde Streamlit. Es el patrón ADAPTADOR: esta función
    # convierte cualquier entrada en bytes y los tres lectores trabajan siempre
    # sobre el mismo tipo. hasattr() permite aceptar "cualquier cosa que tenga
    # .read()" sin conocer su clase (duck typing).
    nombre = _nombre_de(archivo)
    try:
        if isinstance(archivo, (str, Path)):
            return Path(archivo).read_bytes()
        if hasattr(archivo, "seek"):
            archivo.seek(0)  # Por si el archivo ya fue leído antes.
        return archivo.read()
    except OSError as exc:
        # REVISIÓN (C-5): archivo inexistente o sin permisos -> excepción del
        # contrato, en lugar de devolver [] en silencio.
        raise ErrorLecturaFuente(f"No fue posible leer '{nombre}': {exc}") from exc


def _leer_texto(archivo):
    """Lee el archivo como texto UTF-8 (con o sin BOM)."""
    contenido = _leer_bytes(archivo)
    try:
        # REVISIÓN (C-2): se leía con "utf-8". temperatura.csv empieza con un BOM
        # (el carácter invisible ﻿), así que la primera columna se llamaba
        # "﻿id" en lugar de "id". Todos los registros quedaban "sin id" y el
        # resultado era 0 válidos de 623. "utf-8-sig" elimina el BOM si existe.
        return contenido.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise ErrorLecturaFuente(
            f"'{_nombre_de(archivo)}' no está codificado en UTF-8: {exc}"
        ) from exc


def _verificar_columnas(columnas, nombre):
    """Error de estructura global si faltan columnas obligatorias."""
    # REVISIÓN (C-5): antes no se verificaba la estructura. Un archivo sin la
    # columna "valor" producía cientos de motivos "campo faltante", en lugar de
    # un único error claro sobre el archivo.
    faltantes = [c for c in COLUMNAS_OBLIGATORIAS if c not in columnas]
    if faltantes:
        raise ErrorFormatoFuente(
            f"'{nombre}' no tiene las columnas obligatorias: {', '.join(faltantes)}"
        )


def _limpiar_celda(valor):
    """Convierte valores propios de pandas a tipos simples de Python.

    - NaN (celda vacía en Excel) -> None, igual que null en JSON.
    - Fechas -> texto ISO, igual que en CSV y JSON.
    """
    # REVISIÓN (C-6): salida homogénea. Antes una celda vacía de Excel llegaba
    # como NaN (float), mientras que en JSON llega como None.
    if isinstance(valor, float) and math.isnan(valor):
        return None
    if isinstance(valor, (datetime, date)):
        return valor.isoformat()
    return valor


def _registro_uniforme(fila, origen, numero_fila):
    """Salida homogénea: copia de la fila + metadatos de trazabilidad."""
    # REVISIÓN (C-6): se agregan _origen y _fila. Con ellos, un error del reporte
    # dice exactamente en qué archivo y en qué fila está el dato a corregir. La
    # interfaz los muestra como "origen" y "fila".
    registro = {str(clave).strip(): _limpiar_celda(valor) for clave, valor in fila.items()}
    registro["_origen"] = origen
    registro["_fila"] = numero_fila
    return registro


# --------------------------------------------------------------------------
# Lectores
# --------------------------------------------------------------------------
def leer_csv(archivo):
    """C-S12-01: lee un CSV y devuelve una lista de diccionarios."""
    nombre = _nombre_de(archivo)
    texto = _leer_texto(archivo)  # REVISIÓN (C-1, C-2): ruta u objeto archivo; sin BOM.
    if not texto.strip():
        # REVISIÓN (C-5): archivo vacío -> error explícito, no [] silencioso.
        raise ErrorFormatoFuente(f"'{nombre}' está vacío: no tiene encabezado ni registros")

    # csv.DictReader usa la primera línea como nombres de columna.
    # REVISIÓN (C-6): restkey/restval permiten detectar filas con columnas de más
    # o de menos (antes generaban una clave None o valores None sin aviso).
    lector = csv.DictReader(io.StringIO(texto), restkey="_columnas_extra", restval=None)
    _verificar_columnas([c.strip() for c in (lector.fieldnames or [])], nombre)

    registros = []
    # start=2: la fila 1 del archivo es el encabezado.
    for numero_fila, fila in enumerate(lector, start=2):
        extra = fila.pop("_columnas_extra", None)
        registro = _registro_uniforme(fila, nombre, numero_fila)
        # REVISIÓN (C-6): una fila rota se MARCA (el Rol B la reporta) y la
        # lectura continúa: una fila mala no debe impedir leer las otras 622.
        if extra is not None:
            registro["_error_estructura"] = f"Fila con columnas de más: {extra}"
        elif any(valor is None for valor in fila.values()):
            registro["_error_estructura"] = "Fila con columnas de menos"
        registros.append(registro)
    return registros


def leer_json(archivo):
    """C-S12-02: lee un JSON y devuelve una lista de diccionarios.

    Formatos admitidos:
        [ {...}, {...} ]                  lista de registros
        { "registros": [ {...}, ... ] }   objeto contenedor (formato de presion.json)
    """
    nombre = _nombre_de(archivo)
    texto = _leer_texto(archivo)  # REVISIÓN (C-1): ruta u objeto archivo.
    if not texto.strip():
        raise ErrorFormatoFuente(f"'{nombre}' está vacío")
    try:
        datos = json.loads(texto)
    except json.JSONDecodeError as exc:
        # REVISIÓN (C-5): antes `except (json.JSONDecodeError, Exception): return []`.
        raise ErrorFormatoFuente(f"'{nombre}' no es un JSON válido: {exc}") from exc

    # REVISIÓN (C-5): antes, un objeto sin "registros" se devolvía como [datos],
    # es decir, todo el objeto pasaba como si fuera un único registro.
    if isinstance(datos, dict):
        if "registros" not in datos:
            raise ErrorFormatoFuente(f"'{nombre}' es un objeto JSON sin la clave 'registros'")
        datos = datos["registros"]
    if not isinstance(datos, list):
        raise ErrorFormatoFuente(
            f"'{nombre}' debe contener una lista de registros, se encontró {type(datos).__name__}"
        )

    registros = []
    for numero_fila, elemento in enumerate(datos, start=1):
        if isinstance(elemento, dict):
            registros.append(_registro_uniforme(elemento, nombre, numero_fila))
        else:
            # REVISIÓN (C-6): error estructural aislado. Se marca y se sigue con los demás.
            registros.append({
                "_origen": nombre,
                "_fila": numero_fila,
                "_error_estructura": f"Elemento que no es un objeto JSON: {elemento!r}",
            })
    return registros


def leer_excel(archivo):
    """C-S12-03: lee la primera hoja de un Excel y devuelve una lista de diccionarios."""
    # REVISIÓN (C-3): faltaba esta importación. Se hace dentro de la función
    # porque pandas tarda en cargar y solo se necesita para Excel.
    import pandas as pd

    nombre = _nombre_de(archivo)
    contenido = _leer_bytes(archivo)  # REVISIÓN (C-1): ruta u objeto archivo.
    if not contenido:
        raise ErrorFormatoFuente(f"'{nombre}' está vacío")
    try:
        # REVISIÓN (C-6): dtype=object hace que pandas NO convierta los valores:
        # se entregan "crudos" (por ejemplo, "SIN_DATO" se conserva como texto).
        # Decidir qué es un número es tarea del Rol A, no del lector.
        tabla = pd.read_excel(io.BytesIO(contenido), dtype=object)
    except Exception as exc:  # openpyxl/zipfile lanzan varios tipos de error.
        # REVISIÓN (C-3, C-5): antes `except Exception: return []` escondía el
        # NameError. Ahora un archivo dañado produce un error explícito.
        raise ErrorLecturaFuente(f"No fue posible leer el Excel '{nombre}': {exc}") from exc

    _verificar_columnas([str(c).strip() for c in tabla.columns], nombre)

    registros = []
    # start=2: la fila 1 de la hoja es el encabezado.
    for numero_fila, fila in enumerate(tabla.to_dict(orient="records"), start=2):
        registros.append(_registro_uniforme(fila, nombre, numero_fila))
    return registros
