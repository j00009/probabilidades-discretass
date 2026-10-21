# librerias que se van a usar
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from math import comb


###### funciones correspondientes alas formulas del informe
 

# distribucion geometrica
def _validar_p(p):
    if not 0 < p <= 1:
        raise ValueError("p debe cumplir 0 < p <= 1")
 
 
def geom_pmf(k, p):
    """P(X = k) = (1 - p)^(k - 1) * p, con k = 1, 2, 3, ..."""
    _validar_p(p)
    if k < 1:
        return 0.0
    return (1 - p) ** (k - 1) * p
 
 
def geom_cdf(k, p):
    """P(X <= k) = 1 - (1 - p)^k"""
    _validar_p(p)
    if k < 1:
        return 0.0
    return 1 - (1 - p) ** k
 
 
def geom_media(p):
    """E(X) = 1 / p"""
    _validar_p(p)
    return 1 / p
 
 
def geom_varianza(p):
    """Var(X) = (1 - p) / p^2"""
    _validar_p(p)
    return (1 - p) / p**2


# distribucion hipergeometrica



def _validar_hiper(N, K, n):
    if not (0 <= K <= N):
        raise ValueError("Se debe cumplir 0 <= K <= N")
    if not (0 <= n <= N):
        raise ValueError("Se debe cumplir 0 <= n <= N")
 
 
def hiper_rango(N, K, n):
    """Valores posibles de k: max(0, n - (N - K)) <= k <= min(n, K)"""
    _validar_hiper(N, K, n)
    return max(0, n - (N - K)), min(n, K)
 
 
def hiper_pmf(k, N, K, n):
    """P(X = k) = C(K, k) * C(N - K, n - k) / C(N, n)"""
    k_min, k_max = hiper_rango(N, K, n)
    if k < k_min or k > k_max:
        return 0.0
    return comb(K, k) * comb(N - K, n - k) / comb(N, n)
 
 
def hiper_cdf(k, N, K, n):
    """P(X <= k) = suma de P(X = i) para i desde k_min hasta k"""
    k_min, k_max = hiper_rango(N, K, n)
    if k < k_min:
        return 0.0
    return sum(hiper_pmf(i, N, K, n) for i in range(k_min, min(k, k_max) + 1))
 
 
def hiper_media(N, K, n):
    """E(X) = n * K / N"""
    _validar_hiper(N, K, n)
    return n * K / N
 
 
def hiper_varianza(N, K, n):
    """Var(X) = n * (K/N) * (1 - K/N) * (N - n) / (N - 1)"""
    _validar_hiper(N, K, n)
    if N < 2:
        raise ValueError("Se necesita N >= 2 para calcular la varianza")
    return n * (K / N) * (1 - K / N) * (N - n) / (N - 1)
 

## comprobacion rapida


if __name__ == "__main__":
    print("--- Geométrica ---")
    print(f"Ej. 1  P(X=4), p=0,25        = {geom_pmf(4, 0.25):.4f}")
    print(f"Ej. 1  E(X),   p=0,25        = {geom_media(0.25):.4f}")
    print(f"Ej. 2a P(X=3), p=0,8         = {geom_pmf(3, 0.8):.4f}")
    print(f"Ej. 2b P(X<=3), p=0,8        = {geom_cdf(3, 0.8):.4f}")
    print(f"Ej. 2c E(X),   p=0,8         = {geom_media(0.8):.4f}")
 
    print("\n--- Hipergeométrica ---")
    print(f"Ej. 1  P(X=1), N=50,K=5,n=10 = {hiper_pmf(1, 50, 5, 10):.4f}")
    print(f"Ej. 1  E(X)                  = {hiper_media(50, 5, 10):.4f}")
    print(f"Ej. 2a P(X=0), N=20,K=4,n=5  = {hiper_pmf(0, 20, 4, 5):.4f}")
    print(f"Ej. 2b P(X>=1)               = {1 - hiper_pmf(0, 20, 4, 5):.4f}")
    print(f"Ej. 2c E(X)                  = {hiper_media(20, 4, 5):.4f}")
 
    print("\n--- Comprobaciones internas ---")
    # La suma de todas las probabilidades debe ser 1
    k_min, k_max = hiper_rango(20, 4, 5)
    suma = sum(hiper_pmf(k, 20, 4, 5) for k in range(k_min, k_max + 1))
    print(f"Suma de P(X=k) hipergeométrica = {suma:.6f}")
    print(f"P(X<=k_max) hipergeométrica    = {hiper_cdf(k_max, 20, 4, 5):.6f}")
    print(f"Var(X) hiper N=50,K=5,n=10     = {hiper_varianza(50, 5, 10):.4f}  (a mano: 10*0,1*0,9*40/49 = 0,7347)")
 


