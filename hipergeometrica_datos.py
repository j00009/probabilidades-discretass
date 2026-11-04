
import csv
import random
from math import comb
from collections import Counter, defaultdict
from statistics import mean, pvariance


# ============================================================
# VALIDACIONES Y FUNCIONES DE LA DISTRIBUCION HIPERGEOMETRICA
# ============================================================

def validar_parametros(N, K, n):
    if N <= 0:
        raise ValueError("N debe ser mayor que cero.")

    if K < 0 or K > N:
        raise ValueError("K debe estar entre 0 y N.")

    if n < 0 or n > N:
        raise ValueError("n debe estar entre 0 y N.")


def hiper_rango(N, K, n):
    validar_parametros(N, K, n)

    minimo = max(0, n - (N - K))
    maximo = min(n, K)

    return minimo, maximo


def hiper_pmf(k, N, K, n):
    minimo, maximo = hiper_rango(N, K, n)

    if k < minimo or k > maximo:
        return 0.0

    return (
        comb(K, k) * comb(N - K, n - k)
    ) / comb(N, n)


def hiper_media(N, K, n):
    validar_parametros(N, K, n)
    return n * K / N


def hiper_varianza(N, K, n):
    validar_parametros(N, K, n)

    if N < 2:
        return 0.0

    return (
        n
        * (K / N)
        * (1 - K / N)
        * ((N - n) / (N - 1))
    )


# ============================================================
# GENERACION DE DATOS SIMULADOS
# ============================================================

def generar_csv(ruta, N, K, n, experimentos=500, semilla=None):
    validar_parametros(N, K, n)

    if experimentos < 100:
        raise ValueError("Se requieren al menos 100 experimentos.")

    if semilla is not None:
        random.seed(semilla)

    # Se crea una poblacion:
    # Los primeros K elementos son exitos.
    poblacion = list(range(1, N + 1))

    with open(ruta, "w", newline="", encoding="utf-8") as archivo:
        escritor = csv.writer(archivo)

        escritor.writerow([
            "experimento",
            "muestra",
            "elemento",
            "resultado"
        ])

        for experimento in range(1, experimentos + 1):

            # Seleccion sin reemplazo.
            muestra = random.sample(poblacion, n)

            for posicion, elemento in enumerate(muestra, start=1):

                if elemento <= K:
                    resultado = "Exito"
                else:
                    resultado = "Fracaso"

                escritor.writerow([
                    experimento,
                    posicion,
                    elemento,
                    resultado
                ])

    return experimentos * n


# ============================================================
# LECTURA Y VALIDACION DEL CSV
# ============================================================

def leer_resultados(ruta, N, K, n):
    validar_parametros(N, K, n)

    experimentos = defaultdict(list)

    with open(ruta, "r", newline="", encoding="utf-8") as archivo:
        lector = csv.DictReader(archivo)

        columnas = {
            "experimento",
            "muestra",
            "elemento",
            "resultado"
        }

        if not columnas.issubset(lector.fieldnames or []):
            raise ValueError("El CSV no tiene las columnas esperadas.")

        for fila in lector:
            experimento = int(fila["experimento"])
            muestra = int(fila["muestra"])
            elemento = int(fila["elemento"])
            resultado = fila["resultado"]

            if elemento < 1 or elemento > N:
                raise ValueError("Se encontró un elemento fuera de la población.")

            if muestra < 1 or muestra > n:
                raise ValueError("Número de muestra inválido.")

            resultado_esperado = (
                "Exito" if elemento <= K else "Fracaso"
            )

            if resultado != resultado_esperado:
                raise ValueError("Resultado inconsistente con el elemento.")

            experimentos[experimento].append(
                (muestra, elemento, resultado)
            )

    resultados = []

    for numero, registros in sorted(experimentos.items()):

        if len(registros) != n:
            raise ValueError(
                f"El experimento {numero} no contiene exactamente {n} registros."
            )

        elementos = [registro[1] for registro in registros]

        if len(set(elementos)) != n:
            raise ValueError(
                f"El experimento {numero} contiene elementos repetidos."
            )

        posiciones = [registro[0] for registro in registros]

        if sorted(posiciones) != list(range(1, n + 1)):
            raise ValueError(
                f"Las posiciones del experimento {numero} son inválidas."
            )

        exitos = sum(
            1 for registro in registros
            if registro[2] == "Exito"
        )

        resultados.append(exitos)

    if len(resultados) < 100:
        raise ValueError("El archivo debe contener al menos 100 experimentos.")

    return resultados


# ============================================================
# ANALISIS DE LOS RESULTADOS
# ============================================================

def analizar_hipergeometrica(ruta, N, K, n):
    resultados = leer_resultados(ruta, N, K, n)

    cantidad = len(resultados)
    frecuencias = Counter(resultados)

    minimo, maximo = hiper_rango(N, K, n)

    tabla = []

    for k in range(minimo, maximo + 1):

        frecuencia = frecuencias.get(k, 0)
        probabilidad_empirica = frecuencia / cantidad
        probabilidad_teorica = hiper_pmf(k, N, K, n)

        tabla.append({
            "k": k,
            "frecuencia": frecuencia,
            "empirica": probabilidad_empirica,
            "teorica": probabilidad_teorica
        })

    return {
        "N": N,
        "K": K,
        "n": n,
        "experimentos": cantidad,
        "media_observada": mean(resultados),
        "media_teorica": hiper_media(N, K, n),
        "varianza_observada": pvariance(resultados),
        "varianza_teorica": hiper_varianza(N, K, n),
        "tabla": tabla
    }


# ============================================================
# MOSTRAR RESULTADOS
# ============================================================

def resumen_texto(datos):
    lineas = []

    lineas.append(f"Poblacion (N): {datos['N']}")
    lineas.append(f"Exitos en poblacion (K): {datos['K']}")
    lineas.append(f"Tamaño de muestra (n): {datos['n']}")
    lineas.append(f"Experimentos: {datos['experimentos']}")

    lineas.append("")
    lineas.append(
        f"Media observada: {datos['media_observada']:.4f}"
    )
    lineas.append(
        f"Media teorica: {datos['media_teorica']:.4f}"
    )

    lineas.append(
        f"Varianza observada: {datos['varianza_observada']:.4f}"
    )
    lineas.append(
        f"Varianza teorica: {datos['varianza_teorica']:.4f}"
    )

    lineas.append("")
    lineas.append("DISTRIBUCION DE FRECUENCIAS")
    lineas.append("-" * 65)
    lineas.append(
        f"{'k':<8}{'Frecuencia':<15}{'Empirica':<15}{'Teorica':<15}"
    )

    for fila in datos["tabla"]:
        lineas.append(
            f"{fila['k']:<8}"
            f"{fila['frecuencia']:<15}"
            f"{fila['empirica']:<15.4f}"
            f"{fila['teorica']:<15.4f}"
        )

    return "\n".join(lineas)


# ============================================================
# EJECUCION DE LOS TRES EJEMPLOS DEL INFORME
# ============================================================

if __name__ == "__main__":

    escenarios = [
        {
            "nombre": "H1 - Inspeccion de piezas",
            "archivo": "datos_H1_piezas.csv",
            "N": 50,
            "K": 5,
            "n": 10
        },
        {
            "nombre": "H2 - Registros con errores",
            "archivo": "datos_H2_registros.csv",
            "N": 20,
            "K": 4,
            "n": 5
        },
        {
            "nombre": "H3 - Estudiantes sin entrega",
            "archivo": "datos_H3_estudiantes.csv",
            "N": 25,
            "K": 8,
            "n": 6
        }
    ]

    for i, caso in enumerate(escenarios):

        print("\n" + "=" * 65)
        print(caso["nombre"])
        print("=" * 65)

        registros = generar_csv(
            caso["archivo"],
            N=caso["N"],
            K=caso["K"],
            n=caso["n"],
            experimentos=500,
            semilla=42 + i
        )

        print(f"Archivo generado: {caso['archivo']}")
        print(f"Registros individuales: {registros}")

        datos = analizar_hipergeometrica(
            caso["archivo"],
            N=caso["N"],
            K=caso["K"],
            n=caso["n"]
        )

        print()
        print(resumen_texto(datos))

    print("\nProceso finalizado correctamente.")
