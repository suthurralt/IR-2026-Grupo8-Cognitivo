"""
main.py
Test de Intruso Lógico (Odd-One-Out) para rehabilitación cognitiva post-ACV.
Interfaz adaptada para pacientes: botones grandes, alto contraste, sin distracciones.

Uso:
    python main.py

Requisitos:
    pip install -r requirements.txt
    Antes de la primera ejecución: python generate_stimuli.py
"""

import os
import json
import random
import datetime
import sys
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

# --------------------------------------
# CONFIGURACION GENERAL
# --------------------------------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STIMULI_DIR = os.path.join(BASE_DIR, "assets", "stimuli")
RESULTS_DIR = os.path.join(BASE_DIR, "resultados")
IMG_DISPLAY = 200
FONT_TITLE = ("Arial", 22, "bold")
FONT_TEXT = ("Arial", 16)
FONT_BTN = ("Arial", 14, "bold")
COLOR_BG = "#F0F4F8"
COLOR_ACCENT = "#4A90E2"
COLOR_ERR = "#C53030"
COLOR_OK = "#276749"
COLOR_BORDER_SEL = "#E53E3E"

os.makedirs(RESULTS_DIR, exist_ok=True)


def obtener_id_paciente():
    return sys.argv[1].strip() if len(sys.argv) > 1 else ""


# --------------------------------------
# CARGA DE ITEMS
# --------------------------------------
def cargar_items() -> list[dict]:
    """
    Lee los archivos de assets/stimuli y construye la lista de items.
    Cada item: imagenes 0-2 son del grupo, imagen 3 es el intruso.
    """
    items = []
    i = 0
    while True:
        paths = [os.path.join(STIMULI_DIR, f"item{i:02d}_img{j}.png") for j in range(4)]
        if not all(os.path.exists(p) for p in paths):
            break
        items.append({"id": i, "imagenes": paths, "intruso_idx": 3})
        i += 1
    if not items:
        raise FileNotFoundError(
            f"No se encontraron imágenes en '{STIMULI_DIR}'.\n"
            "Ejecutar primero: python generate_stimuli.py"
        )
    return items


# --------------------------------------
# APLICACION PRINCIPAL
# --------------------------------------
class OddOneOutApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Test de Intruso Lógico")
        self.configure(bg=COLOR_BG)
        self.resizable(True, True)
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        # Estado
        self.paciente_id = obtener_id_paciente()
        self.items_originales = cargar_items()
        self.items = []
        self.item_idx = 0
        self.respuestas = []
        self.seleccion = tk.IntVar(value=-1)
        self.imagenes_tk = []
        self.shuffle_map = []
        self.inicio_item = None

        self._pantalla_inicio()

    # ----------------------------------
    # PANTALLA DE INICIO / DATOS
    # ----------------------------------
    def _pantalla_inicio(self):
        self._limpiar()

        # Frame contenedor centrado
        container = tk.Frame(self, bg=COLOR_BG)
        container.pack(expand=True)  # ← esto es la clave

        tk.Label(
            container,
            text="Test de Intruso Lógico",
            font=("Arial", 36, "bold"),
            bg=COLOR_BG,
            fg=COLOR_ACCENT,
        ).pack(pady=(0, 8))

        tk.Label(
            container,
            text="Evaluación de razonamiento inductivo y categorización",
            font=FONT_TEXT,
            bg=COLOR_BG,
            fg="#4A5568",
        ).pack(pady=(0, 30))

        tk.Button(
            container,
            text="Comenzar Test",
            font=FONT_BTN,
            bg=COLOR_ACCENT,
            fg="white",
            activebackground="#2A4A8A",
            relief="flat",
            padx=30,
            pady=14,
            command=self._iniciar_test,
        ).pack()

    # ----------------------------------
    # INICIO DEL TEST
    # ----------------------------------
    def _iniciar_test(self):
        if not self.paciente_id:
            messagebox.showwarning("Atención", "No se pudo obtener el ID del paciente.")
            return

        self.items = self.items_originales.copy()
        random.shuffle(self.items)
        self.item_idx = 0
        self.respuestas = []
        self._mostrar_item()

    # ----------------------------------
    # PANTALLA DE ITEM
    # ----------------------------------
    def _mostrar_item(self):
        self._limpiar()

        if self.item_idx >= len(self.items):
            self._pantalla_resultados()
            return

        item = self.items[self.item_idx]
        self.seleccion.set(-1)
        self.inicio_item = datetime.datetime.now()

        sw = self.winfo_screenwidth()
        sh = self.winfo_screenheight()
        img_size = min(int(sw * 0.18), int(sh * 0.30), 280)

        total = len(self.items)
        prog = f"ítem {self.item_idx + 1} de {total}"
        tk.Label(self, text=prog, font=FONT_TEXT, bg=COLOR_BG, fg="#718096").pack(pady=(int(sh * 0.03), 0))

        bar_w = int(sw * 0.5)
        bar_frame = tk.Frame(self, bg="#CBD5E0", height=10, width=bar_w)
        bar_frame.pack(pady=(6, 0))
        frac = int(bar_w * self.item_idx / total)
        tk.Frame(bar_frame, bg=COLOR_ACCENT, height=10, width=frac).place(x=0, y=0)

        tk.Label(
            self,
            text="¿Cuál de estas imágenes NO pertenece al grupo?",
            font=("Arial", int(sh * 0.030), "bold"),
            bg=COLOR_BG,
            fg="#2D3748",
            wraplength=int(sw * 0.85),
        ).pack(pady=(int(sh * 0.03), int(sh * 0.02)))

        imgs_frame = tk.Frame(self, bg=COLOR_BG)
        imgs_frame.pack(pady=int(sh * 0.01))

        orden = list(range(4))
        random.shuffle(orden)
        self.shuffle_map = orden

        self.imagenes_tk = []
        self._img_labels = []
        self._border_frames = []

        for pos, img_idx in enumerate(orden):
            path = item["imagenes"][img_idx]
            pil_img = Image.open(path).resize((img_size, img_size), Image.LANCZOS)
            tk_img = ImageTk.PhotoImage(pil_img)
            self.imagenes_tk.append(tk_img)

            col_frame = tk.Frame(imgs_frame, bg=COLOR_BG)
            col_frame.grid(row=0, column=pos, padx=int(sw * 0.02))

            border = tk.Frame(col_frame, bg=COLOR_BG, padx=4, pady=4)
            border.pack()
            self._border_frames.append(border)

            img_label = tk.Label(border, image=tk_img, bg=COLOR_BG, cursor="hand2")
            img_label.pack()

            lbl_num = tk.Label(
                col_frame,
                text=str(pos + 1),
                font=("Arial", int(sh * 0.022), "bold"),
                bg=COLOR_BG,
                fg=COLOR_ACCENT,
            )
            lbl_num.pack(pady=6)

            self._img_labels.append(img_label)

            img_label.bind("<Button-1>", lambda e, p=pos: self._seleccionar(p))
            border.bind("<Button-1>", lambda e, p=pos: self._seleccionar(p))
            lbl_num.bind("<Button-1>", lambda e, p=pos: self._seleccionar(p))

        self.btn_confirmar = tk.Button(
            self,
            text="Confirmar selección",
            font=("Arial", int(sh * 0.020), "bold"),
            bg="#A0AEC0",
            fg="white",
            activebackground=COLOR_ACCENT,
            relief="flat",
            padx=36,
            pady=14,
            state="disabled",
            command=self._confirmar,
        )
        self.btn_confirmar.pack(pady=int(sh * 0.03))

        tk.Label(
            self,
            text="Tocá la imagen que creés que NO pertenece al grupo.",
            font=("Arial", int(sh * 0.030)),
            bg=COLOR_BG,
            fg="#4D5663",
        ).pack()

    def _seleccionar(self, pos: int):
        self.seleccion.set(pos)
        for i, border in enumerate(self._border_frames):
            if i == pos:
                border.config(bg=COLOR_BORDER_SEL, padx=4, pady=4)
                self._img_labels[i].config(bg=COLOR_BG)
            else:
                border.config(bg=COLOR_BG, padx=4, pady=4)
                self._img_labels[i].config(bg=COLOR_BG)
        self.btn_confirmar.config(state="normal", bg=COLOR_ACCENT)

    def _confirmar(self):
        pos_seleccionada = self.seleccion.get()
        if pos_seleccionada < 0:
            return

        item = self.items[self.item_idx]
        img_idx_elegida = self.shuffle_map[pos_seleccionada]
        es_correcto = img_idx_elegida == item["intruso_idx"]
        tiempo_ms = int((datetime.datetime.now() - self.inicio_item).total_seconds() * 1000)

        self.respuestas.append(
            {
                "item_id": item["id"],
                "intruso_real": item["intruso_idx"],
                "imagen_elegida": img_idx_elegida,
                "posicion_elegida": pos_seleccionada,
                "correcto": es_correcto,
                "tiempo_ms": tiempo_ms,
            }
        )

        self.item_idx += 1
        self._mostrar_item()

    # ----------------------------------
    # RESULTADOS Y GUARDADO
    # ----------------------------------
    def _pantalla_resultados(self):
        self._limpiar()

        correctas = sum(1 for r in self.respuestas if r["correcto"])
        total = len(self.respuestas)
        pct = int(correctas / total * 100) if total else 0
        tiempo_total = sum(r["tiempo_ms"] for r in self.respuestas)
        tiempo_prom = int(tiempo_total / total) if total else 0

        json_path = self._guardar_json(correctas, total, pct, tiempo_prom)

        tk.Label(
            self,
            text="Test Finalizado",
            font=("Arial", 26, "bold"),
            bg=COLOR_BG,
            fg=COLOR_ACCENT,
        ).pack(pady=(36, 6))

        tk.Label(
            self,
            text=f"ID del paciente: {self.paciente_id}",
            font=("Arial", 18),
            bg=COLOR_BG,
            fg="#4A5568",
        ).pack()

        frame = tk.Frame(self, bg="white", relief="solid", bd=1)
        frame.pack(pady=20, padx=60, fill="x")

        datos = [
            ("Respuestas correctas", f"{correctas} / {total}"),
            ("Porcentaje de acierto", f"{pct} %"),
            ("Tiempo promedio / ítem", f"{tiempo_prom / 1000:.1f} s"),
            ("Tiempo total", f"{tiempo_total / 1000:.1f} s"),
        ]
        for i, (lbl, val) in enumerate(datos):
            bg = "#F7FAFC" if i % 2 == 0 else "white"
            row = tk.Frame(frame, bg=bg)
            row.pack(fill="x")
            tk.Label(row, text=lbl, font=FONT_TEXT, bg=bg, fg="#4A5568", anchor="w").pack(
                side="left", padx=20, pady=8
            )
            tk.Label(row, text=val, font=("Arial", 16, "bold"), bg=bg, fg=COLOR_ACCENT, anchor="e").pack(
                side="right", padx=20, pady=8
            )

        tk.Label(
            self,
            text=f"Resultados guardados en:\n{json_path}",
            font=("Arial", 12),
            bg=COLOR_BG,
            fg="#718096",
            wraplength=600,
            justify="center",
        ).pack(pady=(4, 0))

        btn_frame = tk.Frame(self, bg=COLOR_BG)
        btn_frame.pack(pady=20)

        tk.Button(
            btn_frame,
            text="Nuevo paciente",
            font=FONT_BTN,
            bg=COLOR_ACCENT,
            fg="white",
            activebackground="#2A4A8A",
            relief="flat",
            padx=20,
            pady=10,
            command=self._pantalla_inicio,
        ).pack(side="left", padx=12)

        tk.Button(
            btn_frame,
            text="Salir",
            font=FONT_BTN,
            bg="#718096",
            fg="white",
            activebackground="#4A5568",
            relief="flat",
            padx=20,
            pady=10,
            command=self.destroy,
        ).pack(side="left", padx=12)

    def _guardar_json(self, correctas, total, pct, tiempo_prom) -> str:
        id_seguro = ''.join(
            c if c.isalnum() or c in (' ', '_', '-') else '_' for c in self.paciente_id
        ).replace(' ', '_') or 'sin_id'
        filename = f'{id_seguro}_odd_one_out.json'
        filepath = os.path.join(RESULTS_DIR, filename)

        data = {
            'id_paciente': self.paciente_id,
            'fecha': datetime.datetime.now().isoformat(),
            'total_items': total,
            'respuestas_correctas': correctas,
            'porcentaje': pct,
            'tiempo_promedio_ms': tiempo_prom,
            'respuestas': self.respuestas,
        }

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror('Error al guardar', f'No se pudo guardar el archivo:\n{e}')
        return filepath

    # ----------------------------------
    # UTILIDADES
    # ----------------------------------
    def _limpiar(self):
        for widget in self.winfo_children():
            widget.destroy()
        self.imagenes_tk = []


# --------------------------------------
# ENTRY POINT
# --------------------------------------
if __name__ == '__main__':
    if not os.path.exists(STIMULI_DIR) or not any(f.endswith('.png') for f in os.listdir(STIMULI_DIR)):
        print(
            'ERROR: No se encontraron imágenes de estímulos.\n'
            'Ejecutar primero:\n\n    python generate_stimuli.py\n'
        )
        sys.exit(1)

    app = OddOneOutApp()
    app.mainloop()
