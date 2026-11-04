"""
Punto de entrada: calculadora + gráficos + validación en una sola ventana.
Uso:  python main.py
"""
import tkinter as tk
from tkinter import filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from calculadora_gui import (
    App, FONT, AZUL, AZUL_OSC, BLANCO, GRIS_BD, TEXTO, TEXTO_SEC,
    ROJO, lbl, mk_btn, separador, res_val,
)
import graficos
import validaciones


# ─── Pestaña: Gráficos ─────────────────────────────────────────────────────────
class TabGraficos(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BLANCO)
        self._canvas = None
        self._fig = None
        self._actual = 0

        lbl(self, "Gráficos", bold=True, size=14, color=AZUL
            ).pack(pady=(20, 2), padx=32, anchor="w")
        lbl(self, "Funciones de probabilidad y comparación con la binomial",
            size=10, color=TEXTO_SEC).pack(pady=(0, 8), padx=32, anchor="w")
        separador(self)

        barra = tk.Frame(self, bg=BLANCO)
        barra.pack(fill="x", padx=32, pady=10)

        self._botones = []
        for i, (nombre, _, _) in enumerate(graficos.FIGURAS):
            b = tk.Button(barra, text=nombre, font=(FONT, 10, "bold"),
                          relief="flat", cursor="hand2", padx=14, pady=6,
                          bd=0, command=lambda i=i: self._mostrar(i))
            b.pack(side="left", padx=(0, 8))
            self._botones.append(b)

        mk_btn(barra, "Guardar PNG", self._guardar
               ).pack(side="right")

        self._area = tk.Frame(self, bg=BLANCO)
        self._area.pack(fill="both", expand=True, padx=32, pady=(0, 16))

        self._refrescar_botones()
        # La figura se dibuja la primera vez que se abre la pestaña
        self.bind("<Map>", self._al_mostrar)

    def _al_mostrar(self, _event):
        if self._canvas is None:
            self._mostrar(0)

    def _mostrar(self, i):
        self._actual = i
        if self._canvas is not None:
            self._canvas.get_tk_widget().destroy()
        self._fig = graficos.FIGURAS[i][1]()
        self._canvas = FigureCanvasTkAgg(self._fig, master=self._area)
        self._canvas.draw()
        self._canvas.get_tk_widget().pack(fill="both", expand=True)
        self._refrescar_botones()

    def _refrescar_botones(self):
        for i, b in enumerate(self._botones):
            if i == self._actual:
                b.config(bg=AZUL, fg=BLANCO)
            else:
                b.config(bg=BLANCO, fg=TEXTO,
                         highlightthickness=1, highlightbackground=GRIS_BD)

    def _guardar(self):
        if self._fig is None:
            return
        ruta = filedialog.asksaveasfilename(
            defaultextension=".png",
            initialfile=graficos.FIGURAS[self._actual][2],
            filetypes=[("Imagen PNG", "*.png")])
        if ruta:
            self._fig.savefig(ruta, dpi=200)
            messagebox.showinfo("Guardado", f"Figura guardada en:\n{ruta}")


# ─── Pestaña: Validación ───────────────────────────────────────────────────────
class TabValidacion(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg=BLANCO)

        lbl(self, "Validación con SciPy", bold=True, size=14, color=AZUL
            ).pack(pady=(24, 2), padx=32, anchor="w")
        lbl(self, "Compara las funciones propias con scipy.stats "
                  "(pmf, cdf, media y varianza)",
            size=10, color=TEXTO_SEC).pack(pady=(0, 12), padx=32, anchor="w")
        separador(self)

        mk_btn(self, "  Ejecutar validación  ", self._ejecutar
               ).pack(pady=16, padx=40, anchor="w")
        separador(self)

        frm = tk.Frame(self, bg=BLANCO)
        frm.pack(fill="x", padx=40, pady=14)
        filas = [("Geométrica (dif. máx.)",      "geom"),
                 ("Hipergeométrica (dif. máx.)", "hiper"),
                 ("Resultado",                   "estado")]
        self._rv = {}
        for r, (nombre, key) in enumerate(filas):
            lbl(frm, f"{nombre}:", bold=True, size=11, bg=BLANCO
                ).grid(row=r, column=0, sticky="w", pady=6, padx=(0, 16))
            v = tk.StringVar(value="—")
            res_val(frm, v, r, 1)
            self._rv[key] = v

        self._err = lbl(self, "", color=ROJO, size=10, bg=BLANCO)
        self._err.pack(pady=4, padx=40, anchor="w")

        lbl(self, "Convergencia a la binomial  (P(X=1), n=10)",
            bold=True, size=11, bg=BLANCO
            ).pack(pady=(10, 4), padx=40, anchor="w")
        self._txt = tk.Text(self, height=6, width=48,
                            font=("Courier", 11), relief="solid", bd=1,
                            bg="#f8f9fa", fg=TEXTO)
        self._txt.pack(padx=40, anchor="w")
        self._txt.config(state="disabled")

    def _ejecutar(self):
        self._err.config(text="")
        try:
            dg = validaciones.validar_geometrica()
            dh = validaciones.validar_hipergeometrica()
            tabla = validaciones.tabla_convergencia_texto()
        except Exception as e:
            self._err.config(text=f"⚠  {e}")
            return
        self._rv["geom"].set(f"{dg:.2e}")
        self._rv["hiper"].set(f"{dh:.2e}")
        ok = max(dg, dh) < validaciones.TOLERANCIA
        self._rv["estado"].set("OK" if ok else "REVISAR")
        self._txt.config(state="normal")
        self._txt.delete("1.0", "end")
        self._txt.insert("1.0", tabla)
        self._txt.config(state="disabled")


# ─── Programa principal ────────────────────────────────────────────────────────
def main():
    app = App(extra_tabs=[
        ("  Gráficos  ",   TabGraficos),
        ("  Validación  ", TabValidacion),
    ])
    app.mainloop()


if __name__ == "__main__":
    main()