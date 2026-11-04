
from math import comb


###### funciones correspondientes a las formulas del informe
 

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
    print(f"G1  P(X=3),  p=0,20          = {geom_pmf(3, 0.20):.4f}")
    print(f"G2  P(X<=4), p=0,30          = {geom_cdf(4, 0.30):.4f}")
    print(f"G3  E(X),    p=0,25          = {geom_media(0.25):.4f}")
    print(f"G3  Var(X),  p=0,25          = {geom_varianza(0.25):.4f}")
    print(f"G3  sigma,   p=0,25          = {geom_varianza(0.25) ** 0.5:.2f}")

    print("\n--- Hipergeométrica ---")
    print(f"H1  P(X=1), N=50,K=5,n=10    = {hiper_pmf(1, 50, 5, 10):.4f}")
    print(f"H2  P(X=0), N=20,K=4,n=5     = {hiper_pmf(0, 20, 4, 5):.4f}")
    print(f"H3  P(X=2), N=25,K=8,n=6     = {hiper_pmf(2, 25, 8, 6):.4f}")