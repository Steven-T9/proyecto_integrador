"""Orquestación del procesamiento.

Semana 10–12: completar integración con validación y excepciones.
La clasificación permanece centralizada en clasificacion.py.
"""
from src.processing.clasificacion import clasificar_valor

def procesar_registros(registros):
    # TODO B-S10-01: coordinar normalización y validación sin duplicar reglas.
    # TODO B-S10-02: clasificar únicamente registros válidos.
    # TODO B-S10-03: devolver el contrato común definido en docs/contratos_modulos.md.
    # TODO B-S11-04: aislar errores por registro y continuar el lote.
    # TODO B-S12-04: integrar entradas de lectores CSV, JSON y Excel.
    # La función clasificar_valor(valor, tipo) debe reutilizarse.
    raise NotImplementedError("Pendiente: integración del procesamiento, semanas 10–12")

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