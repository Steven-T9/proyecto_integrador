"""Rol B: excepciones propias de DataLab y reporte de incidencias.

¿Por qué crear excepciones propias en lugar de usar ValueError o Exception?
- Permiten capturar SOLO los errores de DataLab con `except DataLabError`,
  sin ocultar errores de programación inesperados.
- El nombre de la clase ya explica qué pasó (ErrorLecturaFuente, ErrorConversion...).
- Cada clase define su `categoria`, que se usa en el reporte y en los gráficos.

Jerarquía:
    DataLabError
    ├── ErrorValidacion       (reservada: la calidad se informa con motivos, no con excepciones)
    ├── ErrorFormatoFuente    estructura inesperada (columnas, JSON, fila mal formada)
    ├── ErrorLecturaFuente    el archivo no se pudo leer (corrupto, codificación, permisos)
    ├── ErrorConversion       un valor no se pudo convertir al tipo esperado
    └── ErrorEventoSensor     el sensor reportó una falla técnica (SIMULACION_*)

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
from datetime import datetime, timezone

# REVISIÓN (B-8): las cuatro clases estaban definidas dos veces (la versión de
# la plantilla y la del estudiante). Se deja una sola definición de cada una.
#
# REVISIÓN (B-4): al final de este archivo se había pegado la función
# `procesar_lote_datos`, una segunda versión del procesamiento que importaba
# este mismo módulo y los de validación y clasificación. Nadie la llamaba: la
# aplicación usaba procesar_registros (procesamiento.py), que ignoraba estas
# excepciones y crear_reporte_error. Se retiró de aquí y sus buenas ideas
# (excepciones propias, reporte normalizado) se integraron en procesamiento.py.


# REVISIÓN (B-6): cada excepción define su `categoria` como atributo de clase.
# Antes la categoría se calculaba con cadenas if/elif (o no se calculaba). Así,
# cada excepción "sabe" su categoría y las subclases la heredan o la redefinen.
class DataLabError(Exception):
    """Excepción base de la aplicación."""

    categoria = "PROCESAMIENTO"


class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""

    categoria = "VALIDACION"


class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""

    categoria = "ESTRUCTURA"


class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""

    categoria = "LECTURA"


class ErrorConversion(DataLabError):
    """No fue posible convertir un valor al tipo esperado (por ejemplo, texto a número)."""

    categoria = "CONVERSION"


# REVISIÓN (B-5): nueva excepción para las fallas técnicas del sensor.
class ErrorEventoSensor(DataLabError):
    """El registro trae una marca de falla técnica del sensor.

    A diferencia de las otras clases, la categoría depende del evento, por eso
    se recibe en el constructor y se guarda en la instancia.
    """

    def __init__(self, mensaje, categoria):
        super().__init__(mensaje)
        self.categoria = categoria


# --------------------------------------------------------------------------
# Eventos técnicos simulados (columna observacion_tecnica de los datasets)
# --------------------------------------------------------------------------
# REVISIÓN (B-5): los datasets traen eventos SIMULACION_* que el procesamiento
# ignoraba: esos registros terminaban como VÁLIDOS (0 errores técnicos frente a
# los 19 esperados). Un registro con uno de estos marcadores NO es un dato de
# mala calidad: es una lectura que el sensor no pudo completar. Por eso va a
# `errores` y no a `registros_invalidos`.
# La tabla permite agregar un evento nuevo sin tocar el ciclo de procesamiento.
EVENTOS_TECNICOS = {
    "SIMULACION_TIMEOUT_SENSOR": ("TIMEOUT_SENSOR", "El sensor no respondió a tiempo"),
    "SIMULACION_LECTURA_INTERMITENTE": ("LECTURA_INTERMITENTE", "La lectura del sensor fue intermitente"),
    "SIMULACION_PAQUETE_INCOMPLETO": ("PAQUETE_INCOMPLETO", "El paquete de datos llegó incompleto"),
}


def verificar_evento_tecnico(registro):
    """Lanza ErrorEventoSensor si el registro trae un marcador de falla técnica."""
    # REVISIÓN (B-5): función nueva, llamada desde procesamiento.py.
    observacion = registro.get("observacion_tecnica")
    if not isinstance(observacion, str) or not observacion.strip():
        return  # Sin observación: no hay evento técnico.
    marcador = observacion.strip().upper()
    if marcador in EVENTOS_TECNICOS:
        categoria, descripcion = EVENTOS_TECNICOS[marcador]
        raise ErrorEventoSensor(f"{descripcion} ({marcador})", categoria)
    if marcador.startswith("SIMULACION_"):
        # Marcador de simulación no catalogado: también es una falla técnica.
        raise ErrorEventoSensor(f"Evento técnico no catalogado ({marcador})", "EVENTO_TECNICO")


def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO", fila=None):
    """Construye el diccionario estándar de una incidencia técnica.

    B-S11-01: estructura única para todos los errores (facilita tablas y CSV).
    B-S11-02: incluye fecha/hora UTC y categoría sin ocultar el mensaje original.
    B-S11-03: esta función SOLO construye el reporte; la continuidad del lote se
              garantiza en procesamiento.py con try/except dentro del ciclo.
    """
    # REVISIÓN (B-7): se agrega `fila`, que con `origen` permite ubicar el dato
    # exacto en el archivo.
    # REVISIÓN (B-8): datetime.utcnow() está obsoleto desde Python 3.12; se usa
    # datetime.now(timezone.utc). timespec="seconds" quita los microsegundos,
    # así la fecha es más legible en la tabla y en el CSV que se descarga.
    return {
        "id": identificador,
        "categoria": categoria,
        "origen": origen,
        "fila": fila,
        "mensaje": str(mensaje),
        "fecha_hora_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
