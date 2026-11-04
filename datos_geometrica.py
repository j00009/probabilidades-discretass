
"""
Datos para la distribucion geometrica.

G1: Primer exito exactamente en el intento 3. p = 0.20
G2: Primer exito dentro de los primeros 4 intentos. p = 0.30
G3: Calculo de media y varianza. p = 0.25

Se generan 500 experimentos independientes por escenario.
"""

import csv
import random
from collections import Counter
from statistics import mean, pvariance

from distribuciones import (
    geom_pmf,
    geom_cdf,
    geom_media,
    geom_varianza
)


MINIMO_EXPERIMENTOS = 100


# ============================================================
# 1. VALIDACION DE PARAMETROS
# ============================================================

def validar_p(p):
    if not 0 < p <= 1:
        raise ValueError("p debe cumplir 0 < p <= 1")


# ============================================================
# 2. GENERACION DE EXPERIMENTOS
# ============================================================

def generar_csv(ruta, p, experimentos=500, semilla=None):

    validar_p(p)

    if experimentos < MINIMO_EXPERIMENTOS:
        raise ValueError("Se requieren al menos 100 experimentos.")

    azar = random.Random(semilla)

    with open(ruta, "w", newline="", encoding="utf-8") as archivo:

        escritor = csv.writer(archivo)

        escritor.writerow([
            "experimento",
            "intento",
            "resultado"
        ])

        for experimento in range(1, experimentos + 1):

            intento = 0

            # Cada experimento comienza desde cero.
            # Se repite hasta obtener el primer exito.

            while True:

                intento += 1

                resultado = int(azar.random() < p)

                escritor.writerow([
                    experimento,
                    intento,
                    resultado
                ])

                if resultado == 1:
                    break

    return experimentos


# ============================================================
# 3. LECTURA Y VALIDACION DEL CSV
# ============================================================

def leer_resultados(ruta):

    experimentos = {}

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:

        lector = csv.DictReader(archivo)

        columnas = {
            "experimento",
            "intento",
            "resultado"
        }

        if not columnas.issubset(lector.fieldnames or []):
            raise ValueError("El CSV no contiene las columnas esperadas.")

        for fila in lector:

            experimento = int(fila["experimento"])
            intento = int(fila["intento"])
            resultado = int(fila["resultado"])

            if intento < 1:
                raise ValueError("El numero de intento debe ser positivo.")

            if resultado not in (0, 1):
                raise ValueError("El resultado debe ser 0 o 1.")

            if experimento not in experimentos:
                experimentos[experimento] = []

            experimentos[experimento].append(
                (intento, resultado)
            )

    esperas = []

    for numero, registros in sorted(experimentos.items()):

        intentos = [registro[0] for registro in registros]

        if intentos != list(range(1, len(registros) + 1)):
            raise ValueError(
                f"Intentos incorrectos en el experimento {numero}."
            )

        resultados = [registro[1] for registro in registros]

        if resultados[-1] != 1:
            raise ValueError(
                f"El experimento {numero} no termina en exito."
            )

        if 1 in resultados[:-1]:
            raise ValueError(
                f"El experimento {numero} tiene mas de un exito."
            )

        esperas.append(len(registros))

    if len(esperas) < MINIMO_EXPERIMENTOS:
        raise ValueError("Se requieren al menos 100 experimentos.")

    return esperas


# ============================================================
# 4. ANALISIS DE LA DISTRIBUCION GEOMETRICA
# ============================================================

def analizar_geometrica(ruta, p, minimo=MINIMO_EXPERIMENTOS):

    validar_p(p)

    esperas = leer_resultados(ruta)

    if len(esperas) < minimo:
        raise ValueError(
            f"Se requieren al menos {minimo} experimentos."
        )

    cantidad = len(esperas)

    frecuencias = Counter(esperas)

    kmax = max(esperas)

    tabla = []

    for k in range(1, kmax + 1):

        frecuencia = frecuencias.get(k, 0)

        empirica = frecuencia / cantidad

        teorica = geom_pmf(k, p)

        tabla.append({
            "k": k,
            "frecuencia": frecuencia,
            "empirica": empirica,
            "teorica": teorica
        })

    return {
        "p": p,
        "experimentos": cantidad,
        "esperas": esperas,
        "media_observada": mean(esperas),
        "media_teorica": geom_media(p),
        "varianza_observada": pvariance(esperas),
        "varianza_teorica": geom_varianza(p),
        "probabilidad_G1": geom_pmf(3, p),
        "probabilidad_G2": geom_cdf(4, p),
        "frecuencia_G1": frecuencias.get(3, 0) / cantidad,
        "frecuencia_G2": sum(
            1 for valor in esperas if valor <= 4
        ) / cantidad,
        "tabla": tabla
    }


# ============================================================
# 5. RESUMEN DE RESULTADOS
# ============================================================

def resumen_texto(res):

    lineas = [
        f"Probabilidad de exito (p): {res['p']:.2f}",
        f"Experimentos realizados: {res['experimentos']}",
        "",
        f"Media observada: {res['media_observada']:.4f}",
        f"Media teorica: {res['media_teorica']:.4f}",
        "",
        f"Varianza observada: {res['varianza_observada']:.4f}",
        f"Varianza teorica: {res['varianza_teorica']:.4f}",
        "",
        f"P(X = 3) teorica: {res['probabilidad_G1']:.4f}",
        f"P(X = 3) empirica: {res['frecuencia_G1']:.4f}",
        "",
        f"P(X <= 4) teorica: {res['probabilidad_G2']:.4f}",
        f"P(X <= 4) empirica: {res['frecuencia_G2']:.4f}",
        "",
        f"{'k':<8}{'Frecuencia':<15}{'Empirica':<15}{'Teorica':<15}"
    ]

    for fila in res["tabla"]:

        lineas.append(
            f"{fila['k']:<8}"
            f"{fila['frecuencia']:<15}"
            f"{fila['empirica']:<15.4f}"
            f"{fila['teorica']:<15.4f}"
        )

    return "\n".join(lineas)


# ============================================================
# 6. EJECUCION DE LOS TRES EJEMPLOS DEL INFORME
# ============================================================

if __name__ == "__main__":

    escenarios = [

        {
            "nombre": "G1 - Primer exito exactamente en el intento 3",
            "archivo": "datos_G1_geometrica.csv",
            "p": 0.20
        },

        {
            "nombre": "G2 - Primer exito dentro de los primeros 4 intentos",
            "archivo": "datos_G2_geometrica.csv",
            "p": 0.30
        },

        {
            "nombre": "G3 - Media y varianza de los intentos",
            "archivo": "datos_G3_geometrica.csv",
            "p": 0.25
        }

    ]

    for i, caso in enumerate(escenarios):

        print("\n" + "=" * 70)
        print(caso["nombre"])
        print("=" * 70)

        cantidad = generar_csv(
            ruta=caso["archivo"],
            p=caso["p"],
            experimentos=500,
            semilla=42 + i
        )

        print(f"CSV generado: {caso['archivo']}")
        print(f"Experimentos generados: {cantidad}")

        resultados = analizar_geometrica(
            ruta=caso["archivo"],
            p=caso["p"]
        )

        print()
        print(resumen_texto(resultados))

    print("\nLos tres escenarios finalizaron correctamente.")
