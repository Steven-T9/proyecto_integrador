"""Rol B: orquestación del procesamiento de un lote de registros.

Contrato (docs/contratos_modulos.md):
    procesar_registros(registros) -> dict con las claves
        registros_validos   : registros normalizados, con valor numérico y clasificación
        registros_invalidos : [{"registro": {...}, "motivos": [...]}]  (calidad)
        errores             : incidencias técnicas (ver crear_reporte_error)
        resumen             : indicadores calculados sobre los registros válidos

Flujo por registro (cada paso lo hace el módulo responsable; aquí solo se coordina):

    registro ─► ¿es dict y bien formado? ──no──► errores (ESTRUCTURA)
                    │ sí
                    ▼
               normalizar_registro (Rol A)
                    ▼
               ¿evento técnico SIMULACION_*? ──sí──► errores (TIMEOUT_SENSOR, ...)
                    │ no
                    ▼
               validar_registro (Rol A) ──inválido──► registros_invalidos + motivos
                    │ válido
                    ▼
               convertir_valor + clasificar_valor (centralizada) ──► registros_validos

Diferencia clave entre "inválido" y "error":
- INVÁLIDO: el dato llegó, pero su calidad es mala (vacío, texto, fuera de rango...).
- ERROR: el registro no pudo procesarse por una falla técnica o estructural.

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
from src.exceptions.errores import (
    DataLabError,
    ErrorConversion,
    ErrorFormatoFuente,
    crear_reporte_error,
    verificar_evento_tecnico,
)
from src.processing.clasificacion import clasificar_valor
from src.processing.resumen import generar_resumen
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import convertir_valor, validar_registro

# REVISIÓN (B-4): procesar_registros estaba definida DOS veces en este archivo,
# con contratos distintos. La primera clasificaba sin validar (B-S10-02 lo
# prohíbe) y devolvía claves que no eran las del contrato. Python usaba la
# segunda. Se deja una sola implementación.

ORIGEN_POR_DEFECTO = "memoria"


def _datos_de_traza(registro, posicion):
    """Obtiene (origen, fila, id) para identificar un registro en los reportes.

    Los lectores (Rol C) agregan `_origen` y `_fila`. Si el registro viene de
    memoria o no es un diccionario, se usa la posición dentro del lote.
    """
    # REVISIÓN (B-2): antes el `except` hacía reg.get('id') sin comprobar que
    # reg fuera un diccionario. Con un registro de texto o None, el propio
    # except lanzaba AttributeError y DETENÍA TODO EL LOTE (justo lo que B-S11-04
    # debía evitar). Esta función nunca falla, sea cual sea el registro.
    if not isinstance(registro, dict):
        return ORIGEN_POR_DEFECTO, posicion + 1, f"posición {posicion + 1}"
    origen = registro.get("_origen", ORIGEN_POR_DEFECTO)
    fila = registro.get("_fila", posicion + 1)
    identificador = registro.get("id")
    if identificador is None or str(identificador).strip() == "":
        identificador = f"fila {fila}"
    return origen, fila, str(identificador).strip()


def procesar_registro(registro):
    """Procesa UN registro.

    Devuelve ("valido", registro_clasificado) o ("invalido", {"registro", "motivos"}).
    Lanza DataLabError cuando hay una falla técnica; quien llama decide qué hacer.
    """
    # REVISIÓN (B-2): control de estructura explícito. Un elemento que no es dict
    # (por ejemplo, un número suelto dentro de un JSON) se reporta como
    # ESTRUCTURA con un mensaje claro.
    if not isinstance(registro, dict):
        raise ErrorFormatoFuente(
            f"Se esperaba un diccionario y se recibió {type(registro).__name__}: {registro!r}"
        )
    # REVISIÓN (B-7): los lectores (Rol C) marcan con `_error_estructura` las
    # filas mal formadas (columnas de más o de menos). El Rol C DETECTA y MARCA;
    # el Rol B REPORTA. Una fila rota no impide procesar las demás.
    if registro.get("_error_estructura"):
        raise ErrorFormatoFuente(registro["_error_estructura"])

    # B-S10-01: coordinar normalización y validación SIN duplicar sus reglas.
    normalizado = normalizar_registro(registro)

    # REVISIÓN (B-5): eventos técnicos del sensor -> error técnico, no dato inválido.
    verificar_evento_tecnico(normalizado)

    es_valido, motivos = validar_registro(normalizado)
    if not es_valido:
        # REVISIÓN (B-3): la interfaz docente lee item["registro"] e item["motivos"].
        # Antes los motivos se metían DENTRO del registro, así que la tabla de
        # inválidos de Streamlit mostraba los motivos pero no el id, el tipo ni el
        # valor. Separar "lo que dijo el sensor" de "lo que dijo la revisión"
        # también permite exportar el registro sin campos ajenos.
        return "invalido", {"registro": normalizado, "motivos": motivos}

    # REVISIÓN (B-1): antes se clasificaba el valor tal como llegaba. Desde un
    # CSV el valor es texto ("22.78") y clasificar_valor("22.78", ...) compara
    # texto con número: TypeError. Con el CSV de temperatura, 605 de 623 registros
    # terminaban como error. Ahora se convierte primero con convertir_valor
    # (la misma regla del Rol A, sin duplicarla).
    try:
        normalizado["valor"] = convertir_valor(normalizado["valor"])
    except ValueError as exc:
        # `from exc` conserva el error original como causa (útil para depurar).
        raise ErrorConversion(f"No se pudo convertir el valor {normalizado['valor']!r}: {exc}") from exc

    # B-S10-02: clasificar SOLO registros válidos, reutilizando la regla central.
    normalizado["clasificacion"] = clasificar_valor(normalizado["valor"], normalizado["tipo"])
    return "valido", normalizado


def procesar_registros(registros):
    """Procesa un lote completo sin detenerse por errores individuales."""
    registros_validos = []
    registros_invalidos = []
    errores = []

    for posicion, registro in enumerate(registros):
        # B-S11-04: el try/except va DENTRO del for. Así, si un registro falla,
        # se reporta y el ciclo continúa con el siguiente (continuidad del lote).
        try:
            estado, resultado = procesar_registro(registro)
            if estado == "valido":
                registros_validos.append(resultado)
            else:
                registros_invalidos.append(resultado)
        # REVISIÓN (B-6): antes había un único `except Exception` que guardaba
        # {"registro_original", "motivo"} sin categoría y sin usar
        # crear_reporte_error. Ahora hay dos bloques, en este orden:
        #   1) DataLabError: fallas PREVISTAS, con la categoría de su clase.
        #   2) Exception: red de seguridad para lo IMPREVISTO (posible bug).
        # El orden importa: Python usa el primer except que coincide.
        except DataLabError as exc:
            # REVISIÓN (B-4): se usa crear_reporte_error, que antes no se llamaba.
            origen, fila, identificador = _datos_de_traza(registro, posicion)
            errores.append(crear_reporte_error(origen, identificador, exc, exc.categoria, fila))
        except Exception as exc:  # noqa: BLE001 - red de seguridad del lote
            origen, fila, identificador = _datos_de_traza(registro, posicion)
            mensaje = f"{type(exc).__name__}: {exc}"
            errores.append(crear_reporte_error(origen, identificador, mensaje, "INESPERADO", fila))

    # REVISIÓN (B-8): los indicadores se calculan con generar_resumen (BAJO,
    # NORMAL, ALTO, promedios por sensor) SOLO sobre los válidos, como pide el
    # contrato. Antes el resumen tenía únicamente los conteos del lote.
    resumen = generar_resumen(registros_validos)
    resumen.update({
        "total_recibidos": len(registros),
        "total_validos": len(registros_validos),
        "total_invalidos": len(registros_invalidos),
        "total_errores": len(errores),
    })

    # B-S10-03: contrato común.
    return {
        "registros_validos": registros_validos,
        "registros_invalidos": registros_invalidos,
        "errores": errores,
        "resumen": resumen,
    }
