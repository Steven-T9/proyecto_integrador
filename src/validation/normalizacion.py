"""Rol A: normalización y estandarización de registros.

SEMANA 10: implementar las funciones marcadas TODO.
Contrato: recibir un diccionario y devolver una COPIA normalizada.
No modificar el registro original.
"""
def normalizar_registro(registro):
    # TODO A-S10-01: validar que registro sea un diccionario.
    # TODO A-S10-02: quitar espacios de id, tipo, unidad y valor textual.
    # TODO A-S10-03: estandarizar tipo a minúsculas.
    # TODO A-S10-04: devolver una copia; no convertir aún el valor a float aquí.
    raise NotImplementedError("Pendiente: implementación del rol A, semana 10")

def normalizar_registro(registro):
    # TODO A-S10-01: validar que registro sea un diccionario.
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")
    
    # TODO A-S10-04: devolver una copia; no convertir aún el valor a float aquí.
    # Creamos una copia del diccionario original para no alterarlo
    copia = registro.copy()
    
    # TODO A-S10-02: quitar espacios de id, tipo, unidad y valor textual.
    # TODO A-S10-03: estandarizar tipo a minúsculas.
    if "id" in copia and isinstance(copia["id"], str):
        copia["id"] = copia["id"].strip()
        
    if "tipo" in copia and isinstance(copia["tipo"], str):
        copia["tipo"] = copia["tipo"].strip().lower()  # Quita espacios y pasa a minúsculas
        
    if "unidad" in copia and isinstance(copia["unidad"], str):
        copia["unidad"] = copia["unidad"].strip()
        
    if "valor" in copia and isinstance(copia["valor"], str):
        copia["valor"] = copia["valor"].strip()
        
    return copia
def normalizar_registro(registro):
    """
    Contrato: recibir un diccionario y devolver una COPIA normalizada.
    No modificar el registro original.
    """
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")
    
    # Crear una copia para no alterar el original
    copia = registro.copy()
    
    if "id" in copia and isinstance(copia["id"], str):
        copia["id"] = copia["id"].strip()
        
    if "tipo" in copia and isinstance(copia["tipo"], str):
        copia["tipo"] = copia["tipo"].strip().lower()
        
    if "unidad" in copia and isinstance(copia["unidad"], str):
        copia["unidad"] = copia["unidad"].strip()
        
    if "valor" in copia and isinstance(copia["valor"], str):
        copia["valor"] = copia["valor"].strip()
        
    return copia

# Diccionario de prueba con espacios de sobra y mayúsculas
registro_original = {
    "id": "  A-001  ",
    "tipo": "  TEMPERATURA ",
    "unidad": " °C ",
    "valor": " 25.5 "
}

# Ejecutamos la función
registro_normalizado = normalizar_registro(registro_original)

print("Original:", repr(registro_original))
print("Normalizado:", repr(registro_normalizado))

# Por ultimo un codigo incluyendo el procesimiento y el resultado
def normalizar_registro(registro):
    if not isinstance(registro, dict):
        raise TypeError("El registro debe ser un diccionario.")
    
    copia = registro.copy()
    
    for k in ["id", "unidad", "valor"]:
        if k in copia and isinstance(copia[k], str):
            copia[k] = copia[k].strip()
            
    if "tipo" in copia and isinstance(copia["tipo"], str):
        copia["tipo"] = copia["tipo"].strip().lower()
        
    return copia


# --- Prueba rápida ---
original = {"id": " 01 ", "tipo": " HUMEDAD ", "unidad": " % ", "valor": " 60.5 "}
resultado = normalizar_registro(original)

print("Original:", original)
print("Resultado:", resultado)