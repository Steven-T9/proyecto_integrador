"""Rol A: normalización y estandarización de registros.

Contrato (docs/contratos_modulos.md):
    normalizar_registro(registro) -> dict

- Recibe un diccionario y devuelve una COPIA normalizada.
- NUNCA modifica el registro original (los lectores y las pruebas lo reutilizan).
- NO convierte el valor a float ni decide si el registro es válido:
  eso corresponde a validaciones.py (separación de responsabilidades).

¿Qué significa "normalizar"? Llevar a una forma estándar datos que significan
lo mismo pero están escritos distinto. Ejemplos:
    " TEMPERATURA "  -> "temperatura"
    "Presión"        -> "presion"
    "celsius", "c"   -> "°C"
    " 24,5 "         -> "24.5"   (sigue siendo texto)
    ""  o  NaN       -> None     (dato faltante, sin importar la fuente)

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
import math
import unicodedata

# REVISIÓN (A-1): el archivo tenía normalizar_registro definida CUATRO veces y
# dos bloques de prueba con print() al final. En Python solo sobrevive la última
# definición, y todo el código suelto del módulo se ejecuta cada vez que otro
# archivo hace `import`. Se deja una sola definición y se eliminan los print.

# REVISIÓN (A-3): tabla de equivalencias de unidades -> unidad canónica.
# Antes la normalización solo quitaba espacios y la validación aceptaba
# "celsius" o "c" sin estandarizarlas, así que los registros válidos salían con
# unidades distintas para lo mismo. Las claves van en minúsculas porque se
# comparan contra unidad.lower().
# Solo se incluyen sinónimos de la MISMA unidad. "Pa", "bar" o "atm" NO son
# sinónimos de "hPa" (1 bar = 1000 hPa): necesitarían una conversión numérica,
# por eso se dejan tal cual y validaciones.py los rechaza.
ALIAS_UNIDADES = {
    "°c": "°C",
    "ºc": "°C",  # Con el signo ordinal "º", muy común al escribir en teclado español.
    "c": "°C",
    "celsius": "°C",
    "hpa": "hPa",
    "hectopascal": "hPa",
    "%": "%",
    "porcentaje": "%",
}

# Campos de texto que se limpian de espacios al inicio y al final.
CAMPOS_TEXTO = ("id", "tipo", "unidad", "valor", "fecha", "observacion_tecnica")


def es_vacio(valor):
    """Indica si un valor representa un dato faltante.

    Cada fuente representa "sin dato" de manera distinta:
    - CSV  -> cadena vacía ""
    - JSON -> null (None en Python)
    - Excel/pandas -> NaN (un float especial)
    Esta función unifica los tres casos en una sola pregunta.
    """
    if valor is None:
        return True
    # REVISIÓN (A-4): NaN no se consideraba vacío. Como float("nan") no lanza
    # error, una celda vacía de Excel pasaba la validación numérica y el
    # registro quedaba VÁLIDO. math.isnan detecta ese caso.
    if isinstance(valor, float) and math.isnan(valor):
        return True
    if isinstance(valor, str) and valor.strip() == "":
        return True
    return False


def quitar_tildes(texto):
    """Convierte 'Presión' en 'Presion' (descompone la letra y elimina la tilde)."""
    # REVISIÓN (A-6): antes "Presión".lower() daba "presión", que no está en los
    # tipos permitidos (allí se escribe "presion"), y el registro se rechazaba.
    # NFKD separa "ó" en "o" + tilde; combining() identifica la tilde para quitarla.
    descompuesto = unicodedata.normalize("NFKD", texto)
    return "".join(c for c in descompuesto if not unicodedata.combining(c))


def normalizar_unidad(unidad):
    """Devuelve la unidad canónica si es un sinónimo conocido; si no, la deja igual."""
    # REVISIÓN (A-3): .get(clave, unidad) devuelve la propia unidad cuando no está
    # en la tabla. Normalizar no es aceptar cualquier cosa: lo desconocido llega
    # intacto a la validación, que explica el motivo del rechazo.
    return ALIAS_UNIDADES.get(unidad.lower(), unidad)


def normalizar_valor_texto(valor):
    """Prepara un valor textual para que validaciones.py pueda interpretarlo.

    Solo cambia la coma decimal por punto ("24,5" -> "24.5").
    No convierte a float (TODO A-S10-04): la conversión es parte de la validación.
    """
    # REVISIÓN (A-7): "21,5" se rechazaba como no numérico. La regla es
    # conservadora: solo actúa si hay una coma y ningún punto. "1.013,2" se deja
    # igual y la validación lo rechaza; normalizar no debe inventar datos.
    if valor.count(",") == 1 and "." not in valor:
        return valor.replace(",", ".")
    return valor


def normalizar_registro(registro):
    """Devuelve una copia normalizada del registro (tareas A-S10-01 a A-S10-04)."""
    # A-S10-01: la entrada debe ser un diccionario. Se lanza TypeError (error
    # de programación); procesamiento.py se encarga de reportarlo sin detener el lote.
    if not isinstance(registro, dict):
        raise TypeError(f"El registro debe ser un diccionario, se recibió {type(registro).__name__}.")

    # A-S10-04: trabajar sobre una COPIA. dict(registro) crea un diccionario
    # nuevo; los cambios en `copia` no afectan al `registro` original.
    copia = dict(registro)

    # A-S10-02: quitar espacios en los campos de texto.
    for campo in CAMPOS_TEXTO:
        if campo not in copia:
            continue  # Si falta el campo, lo reportará validaciones.py.
        # REVISIÓN (A-4): "", None y NaN se unifican en None. Así el motivo de
        # rechazo ("Valor faltante") es el mismo sin importar la fuente.
        if es_vacio(copia[campo]):
            copia[campo] = None
        elif isinstance(copia[campo], str):
            copia[campo] = copia[campo].strip()

    # REVISIÓN (A-6): el id puede llegar como número (por ejemplo, desde Excel).
    # Se pasa a texto para que todos los ids tengan el mismo tipo.
    if copia.get("id") is not None:
        copia["id"] = str(copia["id"]).strip()

    # A-S10-03: tipo en minúsculas.
    # REVISIÓN (A-6): además se quitan las tildes ("Presión" -> "presion").
    if isinstance(copia.get("tipo"), str):
        copia["tipo"] = quitar_tildes(copia["tipo"]).lower()

    # REVISIÓN (A-3): estandarizar unidades escritas de formas distintas.
    if isinstance(copia.get("unidad"), str):
        copia["unidad"] = normalizar_unidad(copia["unidad"])

    # REVISIÓN (A-7): valores textuales con coma decimal (frecuentes en archivos).
    if isinstance(copia.get("valor"), str):
        copia["valor"] = normalizar_valor_texto(copia["valor"])

    return copia
