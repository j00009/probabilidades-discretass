
"""
Figuras del proyecto (Matplotlib).

Cada funcion devuelve un objeto Figure para mostrarlo
dentro de la interfaz Tkinter o guardarlo como PNG.

Incluye:
- Distribuciones teoricas.
- Comparacion de datos simulados y teoricos.
- Convergencia hipergeometrica vs. binomial.
"""

import csv
import numpy as np
import scipy.stats as stats
from collections import Counter, defaultdict
from matplotlib.figure import Figure

from distribuciones import (
    geom_pmf,
    hiper_pmf,
    hiper_rango
)


# ============================================================
# CONFIGURACION DE ARCHIVOS
# ============================================================

ARCHIVOS_GEOMETRICA = (
    ("G1: p=0.20", "datos_G1_geometrica.csv", 0.20),
    ("G2: p=0.30", "datos_G2_geometrica.csv", 0.30),
    ("G3: p=0.25", "datos_G3_geometrica.csv", 0.25),
)

ARCHIVOS_HIPERGEOMETRICA = (
    ("H1: N=50, K=5, n=10", "datos_H1_piezas.csv", 50, 5, 10),
    ("H2: N=20, K=4, n=5", "datos_H2_registros.csv", 20, 4, 5),
    ("H3: N=25, K=8, n=6", "datos_H3_estudiantes.csv", 25, 8, 6),
)


# ============================================================
# CASOS DE LA TABLA DE CONVERGENCIA
# ============================================================

CASOS_CONVERGENCIA = (
    (50, 5),
    (100, 10),
    (500, 50),
    (1000, 100)
)

N_MUESTRA = 10


def datos_convergencia():
    """Filas de la tabla de convergencia del informe."""

    filas = []

    for N, K in CASOS_CONVERGENCIA:

        filas.append((
            N,
            K,
            N_MUESTRA / N,
            hiper_pmf(1, N, K, N_MUESTRA),
            float(stats.binom.pmf(1, N_MUESTRA, K / N))
        ))

    return filas


# ============================================================
# LECTURA DE DATOS GEOMETRICOS
# ============================================================

def leer_geometrica(ruta):
    """
    Lee los experimentos independientes del CSV geometrico.

    Devuelve una lista con los intentos necesarios para
    obtener el primer exito en cada experimento.
    """

    experimentos = defaultdict(list)

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:

        lector = csv.DictReader(archivo)

        for fila in lector:

            experimento = int(fila["experimento"])
            intento = int(fila["intento"])
            resultado = int(fila["resultado"])

            experimentos[experimento].append(
                (intento, resultado)
            )

    esperas = []

    for numero, registros in sorted(experimentos.items()):

        registros.sort(key=lambda x: x[0])

        resultados = [r[1] for r in registros]

        if not resultados or resultados[-1] != 1:
            raise ValueError(
                f"Experimento {numero} incompleto en {ruta}"
            )

        if 1 in resultados[:-1]:
            raise ValueError(
                f"Experimento {numero} contiene exitos repetidos."
            )

        esperas.append(len(registros))

    if not esperas:
        raise ValueError(f"No hay datos en {ruta}")

    return esperas


# ============================================================
# LECTURA DE DATOS HIPERGEOMETRICOS
# ============================================================

def leer_hipergeometrica(ruta, n):
    """
    Lee los registros hipergeometricos.

    Agrupa las filas por experimento y cuenta los exitos
    encontrados en cada muestra.
    """

    experimentos = defaultdict(list)

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:

        lector = csv.DictReader(archivo)

        for fila in lector:

            experimento = int(fila["experimento"])
            resultado = fila["resultado"]

            experimentos[experimento].append(resultado)

    exitos_por_experimento = []

    for numero, resultados in sorted(experimentos.items()):

        if len(resultados) != n:
            raise ValueError(
                f"Experimento {numero} no contiene {n} registros."
            )

        exitos = sum(
            1 for resultado in resultados
            if resultado.strip().lower() in ("exito", "éxito", "1")
        )

        exitos_por_experimento.append(exitos)

    if not exitos_por_experimento:
        raise ValueError(f"No hay datos en {ruta}")

    return exitos_por_experimento


# ============================================================
# 1. DISTRIBUCION GEOMETRICA TEORICA
# ============================================================

def fig_geometrica():

    fig = Figure(figsize=(7, 4), dpi=100)
    ax = fig.add_subplot(111)

    k = np.arange(1, 16)

    for p, marcador in (
        (0.20, "o"),
        (0.30, "s"),
        (0.25, "^")
    ):

        ax.plot(
            k,
            [geom_pmf(int(i), p) for i in k],
            marker=marcador,
            label=f"p = {p:.2f}"
        )

    ax.set_title("Distribución geométrica: P(X = k)")
    ax.set_xlabel("k (intento del primer éxito)")
    ax.set_ylabel("P(X = k)")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig


# ============================================================
# 2. DISTRIBUCION HIPERGEOMETRICA TEORICA
# ============================================================

def fig_hipergeometrica():

    fig = Figure(figsize=(8, 5), dpi=100)
    ax = fig.add_subplot(111)

    casos = (
        (50, 5, 10, "H1: N=50, K=5, n=10"),
        (20, 4, 5, "H2: N=20, K=4, n=5"),
        (25, 8, 6, "H3: N=25, K=8, n=6")
    )

    ancho = 0.25

    for j, (N, K, n, etiqueta) in enumerate(casos):

        k_min, k_max = hiper_rango(N, K, n)

        k = np.arange(k_min, k_max + 1)

        ax.bar(
            k + (j - 1) * ancho,
            [hiper_pmf(int(i), N, K, n) for i in k],
            width=ancho,
            label=etiqueta
        )

    ax.set_title("Distribución hipergeométrica: P(X = k)")
    ax.set_xlabel("k (éxitos en la muestra)")
    ax.set_ylabel("P(X = k)")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")

    fig.tight_layout()

    return fig


# ============================================================
# 3. CONVERGENCIA HIPERGEOMETRICA VS. BINOMIAL
# ============================================================

def fig_convergencia():

    filas = datos_convergencia()

    hiper = [f[3] for f in filas]
    binom = [f[4] for f in filas]

    x = np.arange(len(filas))

    fig = Figure(figsize=(7, 4), dpi=100)
    ax = fig.add_subplot(111)

    ax.bar(
        x - 0.2,
        hiper,
        width=0.4,
        label="Hipergeométrica"
    )

    ax.bar(
        x + 0.2,
        binom,
        width=0.4,
        label="Binomial"
    )

    ax.set_xticks(x)

    ax.set_xticklabels([
        f"N={f[0]}\n(n/N={f[2]:.0%})"
        for f in filas
    ])

    ax.set_ylabel("P(X = 1)")
    ax.set_title("Hipergeométrica vs. binomial al crecer la población")
    ax.legend()
    ax.grid(alpha=0.3, axis="y")

    fig.tight_layout()

    return fig


# ============================================================
# 4. GEOMETRICA: DATOS SIMULADOS VS. TEORICOS
# ============================================================

def fig_geometrica_simulada():

    fig = Figure(figsize=(9, 5), dpi=100)
    ax = fig.add_subplot(111)

    for etiqueta, ruta, p in ARCHIVOS_GEOMETRICA:

        esperas = leer_geometrica(ruta)

        frecuencias = Counter(esperas)

        total = len(esperas)

        k_max = max(esperas)

        ks = np.arange(1, k_max + 1)

        empiricas = [
            frecuencias.get(int(k), 0) / total
            for k in ks
        ]

        teoricas = [
            geom_pmf(int(k), p)
            for k in ks
        ]

        ax.plot(
            ks,
            empiricas,
            marker="o",
            linestyle="-",
            label=f"{etiqueta} - simulada"
        )

        ax.plot(
            ks,
            teoricas,
            linestyle="--",
            label=f"{etiqueta} - teórica"
        )

    ax.set_title("Distribución geométrica: simulación vs. teoría")
    ax.set_xlabel("Intentos hasta el primer éxito")
    ax.set_ylabel("Probabilidad")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig


# ============================================================
# 5. HIPERGEOMETRICA: DATOS SIMULADOS VS. TEORICOS
# ============================================================

def fig_hipergeometrica_simulada():

    fig = Figure(figsize=(9, 5), dpi=100)
    ax = fig.add_subplot(111)

    for etiqueta, ruta, N, K, n in ARCHIVOS_HIPERGEOMETRICA:

        resultados = leer_hipergeometrica(ruta, n)

        frecuencias = Counter(resultados)

        total = len(resultados)

        k_min, k_max = hiper_rango(N, K, n)

        ks = np.arange(k_min, k_max + 1)

        empiricas = [
            frecuencias.get(int(k), 0) / total
            for k in ks
        ]

        teoricas = [
            hiper_pmf(int(k), N, K, n)
            for k in ks
        ]

        ax.plot(
            ks,
            empiricas,
            marker="o",
            linestyle="-",
            label=f"{etiqueta} - simulada"
        )

        ax.plot(
            ks,
            teoricas,
            linestyle="--",
            label=f"{etiqueta} - teórica"
        )

    ax.set_title("Distribución hipergeométrica: simulación vs. teoría")
    ax.set_xlabel("Éxitos encontrados en la muestra")
    ax.set_ylabel("Probabilidad")
    ax.legend()
    ax.grid(alpha=0.3)

    fig.tight_layout()

    return fig


# ============================================================
# BOTONES DE LA INTERFAZ
# ============================================================

FIGURAS = (

    (
        "Geométrica",
        fig_geometrica,
        "geometrica_pmf.png"
    ),

    (
        "Hipergeométrica",
        fig_hipergeometrica,
        "hipergeometrica_pmf.png"
    ),

    (
        "Hiper. vs. binomial",
        fig_convergencia,
        "convergencia_binomial.png"
    ),

    (
        "Geométrica simulada",
        fig_geometrica_simulada,
        "geometrica_simulada.png"
    ),

    (
        "Hipergeométrica simulada",
        fig_hipergeometrica_simulada,
        "hipergeometrica_simulada.png"
    ),

)
