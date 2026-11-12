"""Rol A: reglas de validación de calidad de registros."""
TIPOS_PERMITIDOS = {"temperatura", "presion", "humedad"}

def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    # TODO A-S10-05: validar campos obligatorios: id, tipo, valor y unidad.
    # TODO A-S10-06: validar tipo permitido.
    # TODO A-S10-07: validar que valor tenga formato numérico admitido.
    # TODO A-S10-08: definir reglas de unidad por tipo de sensor.
    # TODO A-S10-09: devolver todos los motivos encontrados, no solo el primero.    raise NotImplementedError("Pendiente: implementación del rol A, semana 10")
def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    motivos = []
    
    if not isinstance(registro, dict):
        return False, ["El registro debe ser un diccionario válido."]
    
    # TODO A-S10-05: validar campos obligatorios: id, tipo, valor y unidad.
    campos_obligatorios = ["id", "tipo", "valor", "unidad"]
    for campo in campos_obligatorios:
        if campo not in registro or registro[campo] is None or (isinstance(registro[campo], str) and not registro[campo].strip()):
            motivos.append(f"El campo obligatorio '{campo}' está ausente o vacío.")
            
    # Si faltan campos obligatorios base, se retorna de inmediato para evitar errores en validaciones posteriores
    if motivos:
        return False, motivos

    # TODO A-S10-06: validar tipo permitido (basado en los datasets del proyecto: temperatura, presión, humedad)[cite: 2].
    tipos_permitidos = {"temperatura", "presion", "humedad"}
    tipo_str = str(registro["tipo"]).strip().lower()
    if tipo_str not in tipos_permitidos:
        motivos.append(f"El tipo de sensor '{registro['tipo']}' no está permitido.")

    # TODO A-S10-07: validar que valor tenga formato numérico admitido.
    valor = registro["valor"]
    try:
        float(valor)
    except (ValueError, TypeError):
        motivos.append(f"El valor '{valor}' no tiene un formato numérico admitido.")

    # TODO A-S10-08: definir reglas de unidad por tipo de sensor.
    unidades_por_tipo = {
        "temperatura": {"°c", "c", "celsius"},
        "presion": {"hpa", "pa", "atm", "bar"},
        "humedad": {"%", "porcentaje"}
    }
    
    unidad_str = str(registro["unidad"]).strip().lower()
    if tipo_str in unidades_por_tipo:
        if unidad_str not in unidades_por_tipo[tipo_str]:
            motivos.append(f"La unidad '{registro['unidad']}' no es válida para el tipo de sensor '{tipo_str}'.")

    # TODO A-S10-09: devolver todos los motivos encontrados, no solo el primero.
    es_valido = len(motivos) == 0
    return es_valido, motivos
# Ejemplo de uso directo
resultado, motivos = validar_registro({"id": "1", "tipo": "temperatura", "valor": "abc", "unidad": "°C"})
print(f"¿Es válido?: {resultado}")
print(f"Motivos: {motivos}")    