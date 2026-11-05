"""Rol B: excepciones y registro de incidencias.

Los tipos de excepción y el contrato de reporte están definidos.
El estudiante implementa la estrategia de captura, clasificación y reporte
durante las semanas 11 y 12.
"""
class DataLabError(Exception):
    """Excepción base de la aplicación."""

class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad."""

class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada no corresponde al contrato esperado."""

class ErrorLecturaFuente(DataLabError):
    """No fue posible leer una fuente de datos."""

def crear_reporte_error(origen, identificador, mensaje, categoria="PROCESAMIENTO"):
    # TODO B-S11-01: construir un diccionario de error normalizado.
    # TODO B-S11-02: incluir fecha/hora y categoría sin ocultar el mensaje original.
    # TODO B-S11-03: evitar que el error de un registro interrumpa el lote completo.
    raise NotImplementedError("Pendiente: implementación del rol B, semanas 11–12")

from datetime import datetime

class DataLabError(Exception):
    """Excepción base de la aplicación DataLab."""
    pass

class ErrorValidacion(DataLabError):
    """El registro no cumple las reglas de calidad o rangos esperados."""
    pass

class ErrorFormatoFuente(DataLabError):
    """La estructura de entrada o columnas no corresponden al contrato esperado."""
    pass

class ErrorLecturaFuente(DataLabError):
    """No fue posible leer físicamente una fuente de datos (archivo corrupto o inaccesible)."""
    pass

class ErrorConversion(DataLabError):
    """No fue posible convertir el tipo de dato de un valor (ej. texto a numérico)."""
    pass
def crear_reporte_error(origen: str, identificador: str, mensaje: str, categoria: str = "PROCESAMIENTO") -> dict:
    """
    Construye un diccionario de error normalizado con timestamp y categoría,
    preservando el mensaje original de la excepción.
    """
    return {
        "timestamp": datetime.utcnow().isoformat(),
        "origen": origen,
        "identificador": identificador,
        "categoria": categoria,
        "mensaje": str(mensaje)
    }
from src.exceptions.errores import (
    DataLabError, 
    ErrorValidacion, 
    ErrorFormatoFuente, 
    ErrorConversion, 
    crear_reporte_error
)
from src.validation.normalizacion import normalizar_registro
from src.validation.validaciones import validar_registro
from src.processing.clasificacion import clasificar_valor

def procesar_lote_datos(registros_brutos: list, origen_id: str = "fuente_memoria") -> dict:
    """
    Coordina el procesamiento del lote completo:
    - Normaliza y valida cada registro.
    - Evita que un error individual detenga el lote completo (Control de robustez).
    - Retorna el diccionario con registros válidos, inválidos, errores y resumen.
    """
    registros_validos = []
    registros_invalidos = []
    lista_errores = []

    for idx, reg_bruto in enumerate(registros_brutos):
        identificador = reg_bruto.get("id", f"idx_{idx}")
        try:
            # 1. Control de estructura básica
            if not isinstance(reg_bruto, dict):
                raise ErrorFormatoFuente(f"El registro en la posición {idx} no es un diccionario válido.")

            # 2. Normalización (Rol A)
            reg_normalizado = normalizar_registro(reg_bruto)

            # 3. Control de conversión de tipos / datos
            try:
                valor_original = reg_normalizado.get("valor")
                if valor_original is not None and str(valor_original).strip() != "":
                    valor_convertido = float(valor_original)
                else:
                    raise ErrorConversion("Valor nulo o vacío detectado.")
            except (ValueError, TypeError) as conv_err:
                raise ErrorConversion(f"No se pudo convertir el valor '{valor_original}' a numérico: {conv_err}")

            # 4. Validación de reglas de calidad (Rol A)
            es_valido, motivo_falla = validar_registro(reg_normalizado)
            if not es_valido:
                raise ErrorValidacion(f"Falla de validación: {motivo_falla}")

            # 5. Clasificación centralizada
            tipo_sensor = reg_normalizado.get("tipo", "desconocido")
            clasificacion = clasificar_valor(valor_convertido, tipo_sensor)
            reg_normalizado["clasificacion"] = clasificacion

            # Si todo es correcto, va a válidos
            registros_validos.append(reg_normalizado)

        except DataLabError as e:
            # Captura controlada: registra el error sin detener el bucle del lote
            categoria_error = e.__class__.__name__
            reporte = crear_reporte_error(
                origen=origen_id,
                identificador=identificador,
                mensaje=e,
                categoria=categoria_error
            )
            lista_errores.append(reporte)
            
            # Marcamos el registro como inválido para el reporte general
            reg_invalido = reg_bruto.copy() if isinstance(reg_bruto, dict) else {"id": identificador}
            reg_invalido["motivo_error"] = str(e)
            registros_invalidos.append(reg_invalido)

    # Construcción del resumen final exigido por el contrato
    resumen = {
        "total_procesados": len(registros_brutos),
        "total_validos": len(registros_validos),
        "total_invalidos": len(registros_invalidos),
        "total_errores": len(lista_errores)
    }

    return {
        "registros_validos": registros_validos,
        "registros_invalidos": registros_invalidos,
        "errores": lista_errores,
        "resumen": resumen
    }