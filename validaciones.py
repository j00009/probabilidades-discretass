"""
Validación de distribuciones.py contra SciPy.

Uso por consola:  python validaciones.py
  - imprime la comparación con SciPy y la tabla de convergencia
  - guarda las figuras en ./figuras/
"""
import os
import numpy as np
import scipy.stats as stats

from distribuciones import (
    geom_pmf, geom_cdf, geom_media, geom_varianza,
    hiper_pmf, hiper_cdf, hiper_media, hiper_varianza, hiper_rango,
)
import graficos

TOLERANCIA = 1e-9


def validar_geometrica():
    """Máxima diferencia absoluta frente a scipy.stats.geom."""
    peor = 0.0
    for p in (0.20, 0.25, 0.30, 0.80):
        k = np.arange(1, 21)
        propio_pmf = np.array([geom_pmf(int(i), p) for i in k])
        propio_cdf = np.array([geom_cdf(int(i), p) for i in k])
        peor = max(peor,
                   np.max(np.abs(propio_pmf - stats.geom.pmf(k, p))),
                   np.max(np.abs(propio_cdf - stats.geom.cdf(k, p))),
                   abs(geom_media(p) - stats.geom.mean(p)),
                   abs(geom_varianza(p) - stats.geom.var(p)))
    return float(peor)


def validar_hipergeometrica():
    """Máxima diferencia absoluta frente a scipy.stats.hypergeom."""
    # SciPy usa el mismo orden: hypergeom(M=N, n=K, N=n)
    peor = 0.0
    for N, K, n in ((50, 5, 10), (20, 4, 5), (25, 8, 6)):
        k_min, k_max = hiper_rango(N, K, n)
        k = np.arange(k_min, k_max + 1)
        propio_pmf = np.array([hiper_pmf(int(i), N, K, n) for i in k])
        propio_cdf = np.array([hiper_cdf(int(i), N, K, n) for i in k])
        media, var = stats.hypergeom.stats(N, K, n, moments="mv")
        peor = max(peor,
                   np.max(np.abs(propio_pmf - stats.hypergeom.pmf(k, N, K, n))),
                   np.max(np.abs(propio_cdf - stats.hypergeom.cdf(k, N, K, n))),
                   abs(hiper_media(N, K, n) - media),
                   abs(hiper_varianza(N, K, n) - var))
    return float(peor)


def tabla_convergencia_texto():
    """Tabla de convergencia a la binomial, lista para imprimir o mostrar."""
    lineas = [f"{'N':>6} {'K':>5} {'n/N':>6} {'Hiper':>8} {'Binomial':>9}"]
    for N, K, frac, h, b in graficos.datos_convergencia():
        lineas.append(f"{N:>6} {K:>5} {frac:>6.0%} {h:>8.4f} {b:>9.4f}")
    return "\n".join(lineas)


def guardar_figuras(carpeta="figuras"):
    os.makedirs(carpeta, exist_ok=True)
    for _, crear, archivo in graficos.FIGURAS:
        crear().savefig(os.path.join(carpeta, archivo), dpi=200)


if __name__ == "__main__":
    dg = validar_geometrica()
    dh = validar_hipergeometrica()
    print("Máxima diferencia absoluta frente a SciPy")
    print(f"  Geométrica:       {dg:.2e}")
    print(f"  Hipergeométrica:  {dh:.2e}")
    print("  Resultado:", "OK" if max(dg, dh) < TOLERANCIA else "REVISAR")

    print("\nTabla de convergencia (P(X=1), n=10)")
    print(tabla_convergencia_texto())

    guardar_figuras()
    print("\nFiguras guardadas en ./figuras/")