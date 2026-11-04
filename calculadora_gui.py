"""
Calculadora de Distribuciones Discretas
Geométrica · Hipergeométrica · Ejemplos precargados
"""

import tkinter as tk
from math import sqrt
from distribuciones import (
    geom_pmf, geom_cdf, geom_media, geom_varianza,
    hiper_pmf, hiper_cdf, hiper_media, hiper_varianza, hiper_rango,
)

# ─── Paleta ────────────────────────────────────────────────────────────────────
AZUL       = "#1a73e8"
AZUL_OSC   = "#1558b0"
AZUL_CLARO = "#e8f0fe"
FONDO      = "#f1f3f4"
BLANCO     = "#ffffff"
GRIS_BD    = "#dadce0"
TEXTO      = "#202124"
TEXTO_SEC  = "#5f6368"
VERDE_BG   = "#e6f4ea"
VERDE_FG   = "#137333"
ROJO       = "#c5221f"
FONT       = "Segoe UI"

# Tamaños de fuente base (se escalan en pantalla completa)
_FS = {"sm": 9, "md": 10, "lg": 12, "xl": 14}


# ─── Helpers ───────────────────────────────────────────────────────────────────
def lbl(parent, txt, bold=False, size=10, color=TEXTO, bg=BLANCO):
    return tk.Label(parent, text=txt,
                    font=(FONT, size, "bold" if bold else "normal"),
                    bg=bg, fg=color)

def mk_entry(parent, width=14):
    return tk.Entry(parent, width=width, font=(FONT, 11),
                    relief="solid", bd=1,
                    highlightthickness=1,
                    highlightcolor=AZUL,
                    highlightbackground=GRIS_BD)

def mk_btn(parent, txt, cmd, bg=AZUL, fg=BLANCO):
    return tk.Button(parent, text=txt, command=cmd,
                     font=(FONT, 11, "bold"), bg=bg, fg=fg,
                     activebackground=AZUL_OSC, activeforeground=BLANCO,
                     relief="flat", cursor="hand2",
                     padx=22, pady=8, bd=0)

def separador(parent, color=GRIS_BD, pady=4):
    tk.Frame(parent, bg=color, height=1).pack(fill="x", pady=pady)

def res_val(parent, var, row, col):
    tk.Label(parent, textvariable=var,
             font=(FONT, 11), bg=VERDE_BG, fg=VERDE_FG,
             anchor="w", padx=12, pady=4,
             relief="flat", width=16
             ).grid(row=row, column=col, padx=(10, 0), pady=5, sticky="w")


# ─── Barra de navegación ───────────────────────────────────────────────────────
class NavBar(tk.Frame):
    def __init__(self, parent, tabs, **kw):
        super().__init__(parent, bg=FONDO, **kw)
        self._tabs   = tabs
        self._btns   = []
        self._active = 0

        inner = tk.Frame(self, bg=FONDO)
        inner.pack(pady=10)

        for i, (nombre, _) in enumerate(tabs):
            b = tk.Button(inner, text=nombre,
                          font=(FONT, 11, "bold"),
                          relief="flat", cursor="hand2",
                          padx=22, pady=8, bd=0,
                          command=lambda i=i: self.select(i))
            b.pack(side="left", padx=5)
            self._btns.append(b)

        self._refresh()

    def select(self, idx):
        self._tabs[self._active][1].pack_forget()
        self._active = idx
        self._tabs[idx][1].pack(fill="both", expand=True)
        self._refresh()

    def _refresh(self):
        for i, b in enumerate(self._btns):
            if i == self._active:
                b.config(bg=AZUL, fg=BLANCO,
                         highlightthickness=2,
                         highlightbackground=AZUL_OSC)
            else:
                b.config(bg=BLANCO, fg=TEXTO,
                         highlightthickness=1,
                         highlightbackground=GRIS_BD)


# ─── Contenido centrado (wrapper para las pestañas de cálculo) ─────────────────
class CenteredTab(tk.Frame):
    """Frame que centra su contenido horizontalmente al redimensionar."""
    def __init__(self, parent, **kw):
        super().__init__(parent, bg=BLANCO, **kw)
        # Canvas + scrollbar para scroll vertical
        self._canvas = tk.Canvas(self, bg=BLANCO, highlightthickness=0)
        self._sb     = tk.Scrollbar(self, orient="vertical",
                                    command=self._canvas.yview)
        self._canvas.configure(yscrollcommand=self._sb.set)

        self._sb.pack(side="right", fill="y")
        self._canvas.pack(side="left", fill="both", expand=True)

        # Frame interior centrado
        self.inner = tk.Frame(self._canvas, bg=BLANCO)
        self._win  = self._canvas.create_window(
            (0, 0), window=self.inner, anchor="n")

        self._canvas.bind("<Configure>", self._on_canvas_resize)
        self.inner.bind("<Configure>", self._on_inner_resize)
        self._canvas.bind_all("<MouseWheel>", self._on_wheel)

    def _on_canvas_resize(self, e):
        # Centrar horizontalmente
        self._canvas.coords(self._win, e.width // 2, 10)
        self._canvas.itemconfig(self._win,
                                width=min(e.width, 640))

    def _on_inner_resize(self, e):
        self._canvas.configure(scrollregion=self._canvas.bbox("all"))

    def _on_wheel(self, e):
        self._canvas.yview_scroll(-1 * (e.delta // 120), "units")


# ─── Pestaña: Geométrica ───────────────────────────────────────────────────────
class TabGeometrica(CenteredTab):
    def __init__(self, parent):
        super().__init__(parent)
        self._build(self.inner)

    def _build(self, p):
        lbl(p, "Distribución Geométrica", bold=True, size=14, color=AZUL
            ).pack(pady=(24, 2), padx=32, anchor="w")
        lbl(p, "P(X = k) = (1 − p)^(k−1) · p      k = 1, 2, 3 …",
            size=10, color=TEXTO_SEC).pack(pady=(0, 12), padx=32, anchor="w")
        separador(p)

        # Inputs
        frm = tk.Frame(p, bg=BLANCO)
        frm.pack(fill="x", padx=40, pady=16)

        campos = [
            ("p  — probabilidad de éxito  (0 < p ≤ 1)", "entry_p"),
            ("k  — número de intento  (entero ≥ 1)",     "entry_k"),
        ]
        for r, (txt, attr) in enumerate(campos):
            lbl(frm, txt, size=11, bg=BLANCO
                ).grid(row=r, column=0, sticky="w", pady=8, padx=(0, 20))
            e = mk_entry(frm)
            e.grid(row=r, column=1, pady=8)
            setattr(self, attr, e)

        mk_btn(p, "  Calcular  ", self._calcular
               ).pack(pady=16, padx=40, anchor="w")
        separador(p)

        # Resultados
        frm_r = tk.Frame(p, bg=BLANCO)
        frm_r.pack(fill="x", padx=40, pady=14)

        filas = [("P(X = k)",      "pmf"),
                 ("P(X ≤ k)",      "cdf"),
                 ("E(X) — Media",  "media"),
                 ("Var(X)",        "var")]
        self._rv = {}
        for r, (nombre, key) in enumerate(filas):
            lbl(frm_r, f"{nombre}:", bold=True, size=11, bg=BLANCO
                ).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 16))
            v = tk.StringVar(value="—")
            res_val(frm_r, v, r, 1)
            self._rv[key] = v

        self._err = lbl(p, "", color=ROJO, size=10, bg=BLANCO)
        self._err.pack(pady=6, padx=40, anchor="w")

    def _calcular(self):
        self._err.config(text="")
        for v in self._rv.values():
            v.set("—")
        try:
            p = float(self.entry_p.get().replace(",", "."))
            k = int(self.entry_k.get())
        except ValueError:
            self._err.config(text="⚠  Ingresa valores numéricos válidos.")
            return
        try:
            self._rv["pmf"].set(f"{geom_pmf(k, p):.6f}")
            self._rv["cdf"].set(f"{geom_cdf(k, p):.6f}")
            self._rv["media"].set(f"{geom_media(p):.6f}")
            self._rv["var"].set(f"{geom_varianza(p):.6f}")
        except ValueError as e:
            self._err.config(text=f"⚠  {e}")


# ─── Pestaña: Hipergeométrica ──────────────────────────────────────────────────
class TabHipergeometrica(CenteredTab):
    def __init__(self, parent):
        super().__init__(parent)
        self._build(self.inner)

    def _build(self, p):
        lbl(p, "Distribución Hipergeométrica", bold=True, size=14, color=AZUL
            ).pack(pady=(24, 2), padx=32, anchor="w")
        lbl(p, "P(X = k) = C(K,k) · C(N−K, n−k) / C(N, n)",
            size=10, color=TEXTO_SEC).pack(pady=(0, 12), padx=32, anchor="w")
        separador(p)

        frm = tk.Frame(p, bg=BLANCO)
        frm.pack(fill="x", padx=40, pady=16)

        campos = [
            ("N  — tamaño de la población",  "entry_N"),
            ("K  — éxitos en la población",  "entry_K"),
            ("n  — tamaño de la muestra",    "entry_n"),
            ("k  — éxitos observados",       "entry_k"),
        ]
        for r, (txt, attr) in enumerate(campos):
            lbl(frm, txt, size=11, bg=BLANCO
                ).grid(row=r, column=0, sticky="w", pady=8, padx=(0, 20))
            e = mk_entry(frm)
            e.grid(row=r, column=1, pady=8)
            setattr(self, attr, e)

        mk_btn(p, "  Calcular  ", self._calcular
               ).pack(pady=16, padx=40, anchor="w")
        separador(p)

        frm_r = tk.Frame(p, bg=BLANCO)
        frm_r.pack(fill="x", padx=40, pady=14)

        filas = [("Rango válido de k",  "rango"),
                 ("P(X = k)",           "pmf"),
                 ("P(X ≤ k)",           "cdf"),
                 ("E(X) — Media",       "media"),
                 ("Var(X)",             "var")]
        self._rv = {}
        for r, (nombre, key) in enumerate(filas):
            lbl(frm_r, f"{nombre}:", bold=True, size=11, bg=BLANCO
                ).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 16))
            v = tk.StringVar(value="—")
            res_val(frm_r, v, r, 1)
            self._rv[key] = v

        self._err = lbl(p, "", color=ROJO, size=10, bg=BLANCO)
        self._err.pack(pady=6, padx=40, anchor="w")

    def _calcular(self):
        self._err.config(text="")
        for v in self._rv.values():
            v.set("—")
        try:
            N = int(self.entry_N.get())
            K = int(self.entry_K.get())
            n = int(self.entry_n.get())
            k = int(self.entry_k.get())
        except ValueError:
            self._err.config(text="⚠  Todos los valores deben ser enteros.")
            return
        try:
            k_min, k_max = hiper_rango(N, K, n)
            self._rv["rango"].set(f"[{k_min},  {k_max}]")
            self._rv["pmf"].set(f"{hiper_pmf(k, N, K, n):.6f}")
            self._rv["cdf"].set(f"{hiper_cdf(k, N, K, n):.6f}")
            self._rv["media"].set(f"{hiper_media(N, K, n):.6f}")
            self._rv["var"].set(f"{hiper_varianza(N, K, n):.6f}")
        except (ValueError, ZeroDivisionError) as e:
            self._err.config(text=f"⚠  {e}")


# ─── Pestaña: Ejemplos precargados ─────────────────────────────────────────────
class TabEjemplos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BLANCO)
        self._build()

    def _build(self):
        # Canvas scrollable
        canvas = tk.Canvas(self, bg=BLANCO, highlightthickness=0)
        sb     = tk.Scrollbar(self, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=sb.set)
        sb.pack(side="right", fill="y")
        canvas.pack(side="left", fill="both", expand=True)

        inner  = tk.Frame(canvas, bg=BLANCO)
        win_id = canvas.create_window((0, 0), window=inner, anchor="n")

        def on_canvas(e):
            canvas.coords(win_id, e.width // 2, 10)
            canvas.itemconfig(win_id, width=min(e.width, 760))
        canvas.bind("<Configure>", on_canvas)
        inner.bind("<Configure>",
                   lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind_all("<MouseWheel>",
                        lambda e: canvas.yview_scroll(-1*(e.delta//120), "units"))

        # ── Cabecera ─────────────────────────────────
        lbl(inner, "Ejemplos del informe", bold=True, size=14, color=AZUL
            ).pack(pady=(24, 2), padx=32, anchor="w")
        lbl(inner, "Resultados precargados desde distribuciones.py",
            size=10, color=TEXTO_SEC).pack(pady=(0, 12), padx=32, anchor="w")
        separador(inner)

        # ── Calcular valores ─────────────────────────
        k_min_h, k_max_h = hiper_rango(20, 4, 5)
        suma_h = sum(hiper_pmf(k, 20, 4, 5) for k in range(k_min_h, k_max_h + 1))

        def fmt(x):
            return f"{x:.4f}  ({x*100:.2f} %)"

        geom_rows = [
            ("G1   P(X=3)",   "p=0.20, k=3",  fmt(geom_pmf(3, 0.20))),
            ("G2   P(X≤4)",   "p=0.30, k=4",  fmt(geom_cdf(4, 0.30))),
            ("G3   E(X)",     "p=0.25",       f"{geom_media(0.25):.4f}"),
            ("G3   Var(X)",   "p=0.25",       f"{geom_varianza(0.25):.4f}"),
            ("G3   σ",        "p=0.25",       f"{sqrt(geom_varianza(0.25)):.2f}"),
        ]
        hiper_rows = [
            ("H1   P(X=1)",   "N=50, K=5, n=10, k=1",  fmt(hiper_pmf(1, 50, 5, 10))),
            ("H2   P(X=0)",   "N=20, K=4, n=5,  k=0",  fmt(hiper_pmf(0, 20, 4, 5))),
            ("H3   P(X=2)",   "N=25, K=8, n=6,  k=2",  fmt(hiper_pmf(2, 25, 8, 6))),
        ]
        comp_rows = [
            ("Σ P(X=k) hipergeométrica",    "N=20, K=4, n=5",   f"{suma_h:.6f}"),
            ("P(X≤k_max) hipergeométrica",  "N=20, K=4, n=5",   f"{hiper_cdf(k_max_h,20,4,5):.6f}"),
            ("Var(X) hipergeométrica",       "N=50, K=5, n=10",  f"{hiper_varianza(50,5,10):.4f}"),
        ]

        self._seccion(inner, "Geométrica")
        self._tabla(inner, ["Ejemplo", "Parámetros", "Resultado"], geom_rows)

        self._seccion(inner, "Hipergeométrica")
        self._tabla(inner, ["Ejemplo", "Parámetros", "Resultado"], hiper_rows)

        self._seccion(inner, "Comprobaciones internas")
        self._tabla(inner, ["Comprobación", "Parámetros", "Resultado"], comp_rows)

        tk.Label(inner, text="", bg=BLANCO).pack(pady=12)

    def _seccion(self, p, titulo):
        f = tk.Frame(p, bg=BLANCO)
        f.pack(fill="x", padx=32, pady=(18, 4))
        tk.Label(f, text=titulo, font=(FONT, 12, "bold"),
                 bg=BLANCO, fg=AZUL).pack(anchor="w")
        tk.Frame(f, bg=AZUL_CLARO, height=2).pack(fill="x", pady=(4, 0))

    def _tabla(self, p, headers, rows):
        frm = tk.Frame(p, bg=BLANCO)
        frm.pack(fill="x", padx=32, pady=(4, 0))
        frm.columnconfigure(0, weight=4)
        frm.columnconfigure(1, weight=3)
        frm.columnconfigure(2, weight=2)

        # Cabecera
        for c, h in enumerate(headers):
            tk.Label(frm, text=h, font=(FONT, 10, "bold"),
                     bg=FONDO, fg=TEXTO_SEC,
                     anchor="w", padx=10, pady=5
                     ).grid(row=0, column=c, sticky="ew", padx=2, pady=(0, 2))

        # Filas
        for r, cols in enumerate(rows, start=1):
            bg_row = BLANCO if r % 2 == 0 else "#f8f9fa"
            for c, val in enumerate(cols):
                fg  = VERDE_FG if c == 2 else TEXTO
                fnt = (FONT, 11, "bold") if c == 2 else (FONT, 11)
                tk.Label(frm, text=val, font=fnt,
                         bg=bg_row, fg=fg,
                         anchor="w", padx=10, pady=6
                         ).grid(row=r, column=c, sticky="ew", padx=2, pady=1)


# ─── Ventana principal ──────────────────────────────────────────────────────────
class App(tk.Tk):
    def __init__(self, extra_tabs=None):
        super().__init__()
        self.title("Calculadora · Distribuciones Discretas")
        self.configure(bg=FONDO)
        self.minsize(560, 500)
        self.geometry("820x700")
        self.resizable(True, True)
        self.eval("tk::PlaceWindow . center")

        self._fullscreen = False

        # ── Header ───────────────────────────────────
        hdr = tk.Frame(self, bg=AZUL)
        hdr.pack(fill="x")

        tk.Label(hdr, text="Distribuciones Discretas",
                 font=(FONT, 14, "bold"), bg=AZUL, fg=BLANCO
                 ).pack(side="left", padx=20, pady=12)

        # Botón pantalla completa (esquina derecha del header)
        self._btn_fs = tk.Button(
            hdr, text="⛶  Pantalla completa",
            command=self._toggle_fullscreen,
            font=(FONT, 10, "bold"),
            bg=AZUL_OSC, fg=BLANCO,
            activebackground="#0d47a1", activeforeground=BLANCO,
            relief="flat", cursor="hand2",
            padx=14, pady=8, bd=0
        )
        self._btn_fs.pack(side="right", padx=14, pady=8)

        tk.Label(hdr, text="UCM · Análisis de Datos",
                 font=(FONT, 10), bg=AZUL, fg="#a8c7fa"
                 ).pack(side="right", padx=4, pady=14)

        # ── Container ────────────────────────────────
        container = tk.Frame(self, bg=BLANCO)
        container.pack(fill="both", expand=True)

        tab_g = TabGeometrica(container)
        tab_h = TabHipergeometrica(container)
        tab_e = TabEjemplos(container)

        tabs = [
            ("  Geométrica  ",      tab_g),
            ("  Hipergeométrica  ", tab_h),
            ("  Ejemplos  ",        tab_e),
        ]

        for nombre, clase in (extra_tabs or []):
            tabs.append((nombre, clase(container)))

        nav = NavBar(container, tabs)
        nav.pack(fill="x", side="top")
        tab_g.pack(fill="both", expand=True)

        # ── Footer ───────────────────────────────────
        footer = tk.Frame(self, bg=FONDO)
        footer.pack(fill="x")
        tk.Label(footer,
                 text="F11  para pantalla completa  ·  Esc para salir  ·  distribuciones.py",
                 font=(FONT, 8), bg=FONDO, fg="#9aa0a6"
                 ).pack(pady=5)

        # ── Atajos de teclado ────────────────────────
        self.bind("<F11>",  lambda e: self._toggle_fullscreen())
        self.bind("<Escape>", lambda e: self._exit_fullscreen())

    def _toggle_fullscreen(self):
        self._fullscreen = not self._fullscreen
        self.attributes("-fullscreen", self._fullscreen)
        if self._fullscreen:
            self._btn_fs.config(text="✕  Salir de pantalla completa")
        else:
            self._btn_fs.config(text="⛶  Pantalla completa")

    def _exit_fullscreen(self):
        if self._fullscreen:
            self._toggle_fullscreen()


if __name__ == "__main__":
    App().mainloop()
