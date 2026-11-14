"""Punto de entrada de la versión de consola.

Ejecutar desde la raíz del proyecto:
    python -m src.main

Cada cambio de la revisión docente está marcado con "# REVISIÓN (ID)".
El ID corresponde a la observación del informe revision/revision_semanas_10_12.html.
"""
from pathlib import Path

from src.data.carga_datos import cargar_datos
from src.exceptions.errores import DataLabError
from src.interface.consola import mostrar_resumen
from src.processing.procesamiento import procesar_registros

CARPETA_DATOS = Path(__file__).resolve().parents[1] / "data" / "raw"
DATASETS = ("temperatura.csv", "presion.json", "humedad.xlsx")


def mostrar_conteos(nombre, resultado):
    r = resultado["resumen"]
    print(f"\n>>> {nombre}")
    print(
        f"Recibidos: {r['total_recibidos']} | Válidos: {r['total_validos']} | "
        f"Inválidos: {r['total_invalidos']} | Errores técnicos: {r['total_errores']}"
    )


def main():
    # REVISIÓN (G-2): antes main() clasificaba cada registro directamente con
    # clasificar_valor, sin normalizar ni validar: la consola se saltaba el
    # trabajo de los roles A y B. Ahora usa el mismo flujo que Streamlit
    # (cargar_datos -> procesar_registros) y además procesa los tres datasets.

    # 1) Demostración en memoria (funciona desde la semana 10).
    resultado = procesar_registros(cargar_datos())
    mostrar_conteos("Demostración en memoria", resultado)
    mostrar_resumen(resultado["resumen"])

    # 2) Datasets de la semana 12. Si un archivo falla, se informa y se
    #    continúa con el siguiente (misma idea de continuidad del Rol B).
    for nombre in DATASETS:
        try:
            resultado = procesar_registros(cargar_datos(CARPETA_DATOS / nombre))
        except DataLabError as exc:
            print(f"\n>>> {nombre}: no se pudo procesar ({type(exc).__name__}: {exc})")
            continue
        mostrar_conteos(nombre, resultado)
        mostrar_resumen(resultado["resumen"])


if __name__ == "__main__":
    main()
