"""Rol C: selección y unificación de fuentes.

Es el único punto de entrada para obtener registros, sin importar la fuente:
    cargar_datos()                           -> registros en memoria (demostración)
    cargar_datos("data/raw/temperatura.csv") -> lee el archivo según su extensión
    cargar_datos(archivo_subido, "x.json")   -> archivo subido desde Streamlit

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
from pathlib import Path

from src.data.fuentes_memoria import cargar_desde_memoria
from src.data.lectores import leer_csv, leer_excel, leer_json
from src.exceptions.errores import ErrorFormatoFuente

# REVISIÓN (C-8): un diccionario extensión -> lector reemplaza la cadena de if.
# Para soportar un formato nuevo basta con escribir el lector y agregar una línea.
# Se retiró ".xls": el proyecto instala openpyxl, que solo lee .xlsx. Aceptar
# .xls prometía algo que después fallaba (la interfaz tampoco lo ofrece).
LECTORES_POR_EXTENSION = {
    "csv": leer_csv,
    "json": leer_json,
    "xlsx": leer_excel,
}


def cargar_datos(archivo=None, nombre_archivo=""):
    """Carga desde memoria o delega en el lector según la extensión."""
    if archivo is None:
        return cargar_desde_memoria()

    # REVISIÓN (C-8): antes, si se pasaba solo una ruta (sin nombre_archivo), la
    # extensión quedaba vacía y la carga fallaba. Ahora el nombre se toma de la
    # ruta o del atributo .name del archivo subido.
    if not nombre_archivo:
        nombre_archivo = str(archivo) if isinstance(archivo, (str, Path)) else getattr(archivo, "name", "")

    extension = Path(nombre_archivo).suffix.lower().lstrip(".")
    lector = LECTORES_POR_EXTENSION.get(extension)
    if lector is None:
        # REVISIÓN (C-8): antes ValueError genérico. ErrorFormatoFuente es una
        # excepción propia de DataLab (contrato con el Rol B) y se puede
        # capturar con `except DataLabError`.
        soportadas = ", ".join(LECTORES_POR_EXTENSION)
        raise ErrorFormatoFuente(
            f"Extensión no soportada: '{extension or 'sin extensión'}' (soportadas: {soportadas})"
        )
    return lector(archivo)
