"""Cálculo de indicadores a partir de registros clasificados (base común).

Recibe SOLO registros válidos y clasificados (con valor numérico).

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""


def generar_resumen(registros):
    altos = normales = bajos = 0
    suma = 0.0
    existe_alto = False  # Bandera: ¿apareció al menos un valor ALTO?
    por_sensor = {}
    # REVISIÓN (G-1): la consola docente muestra `promedio_por_sensor`, que este
    # módulo no generaba, así que no se mostraba ningún promedio. Un promedio
    # global mezcla °C, hPa y % (362,6 en la demostración) y no tiene sentido
    # físico: el promedio útil es por tipo de sensor. Se usan dos acumuladores
    # por tipo (suma y conteo).
    suma_por_sensor = {}
    conteo_por_sensor = {}

    for registro in registros:
        categoria = registro["clasificacion"]
        valor = float(registro["valor"])
        tipo = registro["tipo"]
        suma += valor

        if categoria == "ALTO":
            altos += 1
            existe_alto = True
        elif categoria == "NORMAL":
            normales += 1
        elif categoria == "BAJO":
            bajos += 1

        por_sensor.setdefault(tipo, {"ALTO": 0, "NORMAL": 0, "BAJO": 0})
        if categoria in por_sensor[tipo]:
            por_sensor[tipo][categoria] += 1

        # REVISIÓN (G-1): acumular por tipo de sensor.
        suma_por_sensor[tipo] = suma_por_sensor.get(tipo, 0.0) + valor
        conteo_por_sensor[tipo] = conteo_por_sensor.get(tipo, 0) + 1

    total = len(registros)
    promedio_por_sensor = {
        tipo: suma_por_sensor[tipo] / conteo_por_sensor[tipo] for tipo in suma_por_sensor
    }
    return {
        "altos": altos, "normales": normales, "bajos": bajos,
        "suma": suma, "existe_alto": existe_alto, "total": total,
        # Se conserva "promedio" para no romper código que ya lo usaba.
        "promedio": suma / total if total else 0.0,
        "promedio_por_sensor": promedio_por_sensor,  # REVISIÓN (G-1)
        "por_sensor": por_sensor,
    }
