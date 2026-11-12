"""Orquestación del procesamiento.

Semana 10–12: completar integración con validación y excepciones.
La clasificación permanece centralizada en clasificacion.py.
"""
from src.processing.clasificacion import clasificar_valor
# Opcional: Importa tus módulos de validación/normalización si ya los tienes separados
# from src.processing.validacion import validar_y_normalizar

def procesar_registros(registros):
    """
    Orquesta la normalización, validación, clasificación y control de errores 
    de un lote de registros (provenientes de CSV, JSON o Excel).
    """
    resultados_exitosos = []
    errores_lote = []

    for idx, registro in enumerate(registros):
        try:
            # TODO B-S10-01: Coordinar normalización y validación sin duplicar reglas.
            # (Aquí puedes llamar a tu función central de validación/normalización)
            if not isinstance(registro, dict):
                raise ValueError(f"El registro en la posición {idx} no tiene un formato válido.")
            
            valor = registro.get("valor")
            tipo = registro.get("tipo")

            if valor is None or tipo is None:
                raise ValueError("Faltan campos obligatorios ('valor' o 'tipo') en el registro.")

            # TODO B-S10-02: Clasificar únicamente registros válidos reutilizando clasificar_valor.
            clasificacion = clasificar_valor(valor, tipo)

            # Estructura del registro procesado exitosamente
            resultados_exitosos.append({
                "indice": idx,
                "estado": "exitoso",
                "datos": registro,
                "clasificacion": clasificacion
            })

        except Exception as e:
            # TODO B-S11-04: Aislar errores por registro y continuar el lote sin detenerlo.
            errores_lote.append({
                "indice": idx,
                "estado": "error",
                "registro_original": registro,
                "error": str(e)
            })

    # TODO B-S10-03: Devolver el contrato común definido en docs/contratos_modulos.md.
    contrato_comun = {
        "total_registros": len(registros),
        "exitosos": len(resultados_exitosos),
        "fallidos": len(errores_lote),
        "resultados": resultados_exitosos,
        "errores": errores_lote
    }

    return contrato_comun

from src.processing.clasificacion import clasificar_valor
from src.validation.normalizacion import normalizar_registro  # Proporcionado por el Rol A
from src.validation.validaciones import validar_registro      # Proporcionado por el Rol A

def procesar_registros(registros):
    """
    Procesa un lote de registros (provenientes de memoria o lectores de archivos),
    coordinando normalización, validación, clasificación y aislamiento de errores.
    """
    registros_validos = []
    registros_invalidos = []
    errores = []
    
    total_procesados = 0
    
    for reg in registros:
        try:
            total_procesados += 1
            
            # TODO B-S10-01: Coordinar normalización y validación sin duplicar reglas
            reg_normalizado = normalizar_registro(reg)
            es_valido, motivos = validar_registro(reg_normalizado)
            
            if es_valido:
                # TODO B-S10-02: Clasificar únicamente registros válidos
                tipo = reg_normalizado.get("tipo")
                valor = reg_normalizado.get("valor")
                clasificacion = clasificar_valor(valor, tipo)
                
                # Crear diccionario con el resultado procesado y su clasificación
                reg_resultado = dict(reg_normalizado)
                reg_resultado["clasificacion"] = clasificacion
                registros_validos.append(reg_resultado)
            else:
                # Almacenar registro inválido junto con los motivos de rechazo
                reg_invalido = dict(reg_normalizado)
                reg_invalido["motivos"] = motivos
                registros_invalidos.append(reg_invalido)
                
        except Exception as e:
            # TODO B-S11-04: Aislar errores por registro y continuar el lote (evita que un fallo detenga todo)
            mensaje_error = f"Error crítico al procesar el registro {reg.get('id', 'N/A')}: {str(e)}"
            errores.append({
                "registro_original": reg,
                "motivo": mensaje_error
            })
            
    # Generar el diccionario de resumen del lote
    resumen = {
        "total_procesados": total_procesados,
        "total_validos": len(registros_validos),
        "total_invalidos": len(registros_invalidos),
        "total_errores": len(errores)
    }
    
    # TODO B-S10-03 & B-S12-04: Devolver el contrato común definido (soporta memoria y archivos CSV/JSON/Excel)
    return {
        "registros_validos": registros_validos,
        "registros_invalidos": registros_invalidos,
        "errores": errores,
        "resumen": resumen
    }
