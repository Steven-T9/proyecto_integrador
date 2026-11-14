"""Rol A: reglas de validación de calidad de registros.

Contrato (docs/contratos_modulos.md):
    validar_registro(registro) -> tuple[bool, list[str]]

- Recibe un registro YA normalizado (ver normalizacion.py).
- Devuelve (es_valido, motivos). Si es válido, motivos es una lista vacía.
- Reporta TODOS los motivos encontrados, no solo el primero (A-S10-09).
- No lanza excepciones por datos de mala calidad: un dato malo no es un error
  del programa, es un resultado esperado que se informa en la lista de motivos.

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
import math

# REVISIÓN (A-1): validar_registro estaba definida dos veces. En la primera, el
# `raise NotImplementedError` había quedado pegado al final de un comentario
# (la línea era un comentario completo), y al final del archivo había un ejemplo
# con print() que se ejecutaba cada vez que otro módulo importaba este archivo.

# --------------------------------------------------------------------------
# Reglas de calidad por tipo de sensor: ÚNICA fuente de verdad.
# --------------------------------------------------------------------------
# REVISIÓN (A-6): TIPOS_PERMITIDOS existía pero la función no lo usaba: creaba
# su propio conjunto y su propio diccionario de unidades (la regla estaba
# repetida). Ahora tipo, unidad y rango están en una sola tabla.
#
# REVISIÓN (A-3): cada tipo admite UNA unidad canónica. Antes se aceptaban
# "pa", "atm" y "bar" para presión sin convertir el valor: 1.013 bar se
# clasificaba como presión BAJA, cuando equivale a 1013 hPa (NORMAL).
#
# REVISIÓN (A-5): rangos de plausibilidad. Indican qué valores puede producir
# un sensor sintético de DataLab. Un valor fuera de ese rango (999, -25,
# 1500, 150...) es un número bien escrito, pero no es una medición creíble.
# Antes esos valores se clasificaban como ALTO o BAJO y distorsionaban el resumen.
# Los rangos se dedujeron de los datasets: las lecturas normales están entre
# 2 y 42 °C, 851 y 1080 hPa, y 5 y 95 %, y todas las incidencias quedan fuera.
#
# OJO: estos rangos NO son los umbrales BAJO/NORMAL/ALTO. Esos están en
# src/processing/clasificacion.py y solo se aplican a registros válidos.
# No son mediciones reales ni estándares regulatorios.
REGLAS_SENSOR = {
    "temperatura": {"unidad": "°C", "minimo": -10.0, "maximo": 60.0},
    "presion": {"unidad": "hPa", "minimo": 800.0, "maximo": 1100.0},
    "humedad": {"unidad": "%", "minimo": 0.0, "maximo": 100.0},
}

# Se deriva de REGLAS_SENSOR para no repetir la lista de tipos en dos lugares.
TIPOS_PERMITIDOS = set(REGLAS_SENSOR)

CAMPOS_OBLIGATORIOS = ("id", "tipo", "valor", "unidad")


def convertir_valor(valor):
    """Convierte un valor a float o lanza ValueError si no es numérico.

    Se usa en dos lugares (sin duplicar la regla):
    - validar_registro, para decidir si el formato numérico es admitido.
    - procesamiento.py, para guardar el valor como número en los válidos.
    """
    # REVISIÓN (A-4): bool es subclase de int en Python (True == 1), así que
    # float(True) da 1.0 y un registro con valor True quedaba VÁLIDO.
    if isinstance(valor, bool):
        raise ValueError("un valor booleano no es una medición")
    if isinstance(valor, (int, float)):
        numero = float(valor)
    elif isinstance(valor, str):
        numero = float(valor)  # float("N/A") lanza ValueError.
    else:
        raise ValueError(f"tipo de dato no admitido ({type(valor).__name__})")
    # REVISIÓN (A-4): float("nan") y float("inf") no lanzan error, pero no son
    # mediciones. isfinite() es False para ambos.
    if not math.isfinite(numero):
        raise ValueError("el valor no es finito")
    return numero


def _es_faltante(valor):
    """Un campo falta si no existe, es None o es texto vacío."""
    return valor is None or (isinstance(valor, str) and valor.strip() == "")


def validar_registro(registro):
    """Contrato: devuelve (es_valido: bool, motivos: list[str])."""
    if not isinstance(registro, dict):
        return False, ["Estructura no válida: el registro no es un diccionario"]

    # REVISIÓN (A-8): todos los motivos siguen el formato "Categoría: detalle".
    # La interfaz agrupa los motivos por el texto anterior a ":", así que todos
    # los de una misma clase deben empezar exactamente igual. Antes cada mensaje
    # tenía una redacción distinta y no se podían contar por tipo de incidencia.
    motivos = []

    # A-S10-05: campos obligatorios.
    for campo in CAMPOS_OBLIGATORIOS:
        if _es_faltante(registro.get(campo)):
            if campo == "valor":
                motivos.append("Valor faltante: el campo 'valor' está vacío")
            else:
                motivos.append(f"Campo obligatorio faltante: '{campo}'")

    # REVISIÓN (A-2): aquí había un `if motivos: return False, motivos`. Si
    # faltaba la unidad, ya no se revisaban el tipo ni el valor, e incumplía
    # A-S10-09 ("devolver todos los motivos"). Ahora se sigue revisando y cada
    # regla solo se aplica si los datos que necesita existen.

    tipo = registro.get("tipo")
    unidad = registro.get("unidad")
    valor = registro.get("valor")

    # A-S10-06: tipo permitido. Solo si existe; si falta ya se reportó arriba.
    # REVISIÓN (A-6): se consulta la tabla única REGLAS_SENSOR. isinstance evita
    # un TypeError si el tipo no es texto (una lista no se puede buscar en un set).
    reglas = None
    if not _es_faltante(tipo):
        if isinstance(tipo, str) and tipo in TIPOS_PERMITIDOS:
            reglas = REGLAS_SENSOR[tipo]
        else:
            permitidos = ", ".join(sorted(TIPOS_PERMITIDOS))
            motivos.append(f"Tipo no permitido: '{tipo}' (permitidos: {permitidos})")

    # A-S10-07: formato numérico admitido.
    # REVISIÓN (A-4): se usa convertir_valor, que también rechaza bool, NaN e inf.
    numero = None
    if not _es_faltante(valor):
        try:
            numero = convertir_valor(valor)
        except ValueError:
            motivos.append(f"Valor no numérico: '{valor}'")

    # A-S10-08: unidad esperada según el tipo de sensor.
    # REVISIÓN (A-3): comparación exacta con la unidad canónica; las variantes
    # válidas ya se estandarizaron en normalizacion.py.
    if reglas is not None and not _es_faltante(unidad) and unidad != reglas["unidad"]:
        motivos.append(
            f"Unidad no válida: '{unidad}' para {tipo} (se espera '{reglas['unidad']}')"
        )

    # REVISIÓN (A-5): rango de plausibilidad. Requiere tipo conocido y valor numérico.
    if reglas is not None and numero is not None:
        if not (reglas["minimo"] <= numero <= reglas["maximo"]):
            motivos.append(
                f"Valor fuera de rango: {numero:g} no está entre "
                f"{reglas['minimo']:g} y {reglas['maximo']:g} para {tipo}"
            )

    # A-S10-09: el registro es válido solo si no se encontró ningún motivo.
    return len(motivos) == 0, motivos
