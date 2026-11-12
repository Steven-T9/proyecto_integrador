# Pruebas por rol
- Rol A: `test_calidad.py`
- Rol B: `test_errores.py` y `test_integracion.py`
- Rol C: `test_lectores.py`

Los estudiantes deben crear pruebas unitarias y casos límite de acuerdo con los contratos. En semana 14 se ejecuta la suite completa.

def validar_registro(r):
    if not isinstance(r, dict): return False, ["No es un diccionario"]
    
    if not all(k in r and str(r[k]).strip() for k in ("id", "tipo", "valor", "unidad")):
        return False, ["Faltan datos obligatorios"]

    t, u, v, motivos = str(r["tipo"]).lower(), str(r["unidad"]).lower(), r["valor"], []

    if t not in {"temperatura", "presion", "humedad"}: motivos.append("Tipo no permitido")
    try: float(v)
    except: motivos.append("Valor no numérico")
    
    unidades = {"temperatura": {"°c", "c"}, "presion": {"hpa", "pa", "bar"}, "humedad": {"%"}}
    if t in unidades and u not in unidades[t]: motivos.append("Unidad incorrecta")

    return not motivos, motivos
    
    print(validar_registro({"id": "S1", "tipo": "temperatura", "valor": 24, "unidad": "°C"}))
print(validar_registro({"id": "S2", "tipo": "velocidad", "valor": "abc", "unidad": "km"}))