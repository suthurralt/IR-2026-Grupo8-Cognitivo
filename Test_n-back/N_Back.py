import json
import os
import random
import csv
import sys
import signal
import time
import tkinter as tk
from tkinter import ttk

# CONFIG
NIVELES = [1, 2, 3]
TRIALS = 10
TIEMPO_ESTIMULO = 1000
TIEMPO_RESPUESTA = 3000
TIEMPO_FEEDBACK = 800

# VARIABLES
n_path= os.path.abspath(os.path.dirname(__file__))
nivel_actual = 0
secuencia = []
ronda = 0
aciertos = 0
errores = 0
tiempos = []
inicio = 0.0
esperando_respuesta = False
id_paciente = None
edad_paciente = None
after_ocultar = None
after_timeout = None
after_avanzar = None
ronda_token = 0


def cancelar_temporizador(nombre):
    callback_id = globals()[nombre]
    if callback_id is not None:
        try:
            root.after_cancel(callback_id)
        except tk.TclError:
            pass
        globals()[nombre] = None


def limpiar_temporizadores():
    cancelar_temporizador("after_ocultar")
    cancelar_temporizador("after_timeout")
    cancelar_temporizador("after_avanzar")


def programar_callback(nombre, delay_ms, callback):
    cancelar_temporizador(nombre)
    globals()[nombre] = root.after(delay_ms, callback)


def obtener_datos_paciente():
    patient_id = sys.argv[1].strip() if len(sys.argv) > 1 else None
    if not patient_id:
        return None, None

    csv_path = os.path.join(os.path.abspath(os.path.dirname(n_path)), "pacientes.csv")
    if not os.path.exists(csv_path):
        return patient_id, None

    with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

        for row in reader:
            clean_row = {k.strip(): (v.strip() if v is not None else "") for k, v in row.items() if k is not None}
            if clean_row.get("ID", "") == patient_id:
                edad = clean_row.get("Edad")
                if not edad and None in row and row[None]:
                    edad = row[None][0].strip()
                return patient_id, edad

    return patient_id, None


def obtener_parent_pid():
    if len(sys.argv) > 2:
        try:
            return int(sys.argv[2])
        except ValueError:
            return None
    return None


id_paciente, edad_paciente = obtener_datos_paciente()
parent_pid = obtener_parent_pid()


def cerrar_aplicacion_completa():
    if parent_pid is not None:
        try:
            os.kill(parent_pid, signal.SIGTERM)
        except OSError:
            pass
    root.destroy()


def guardar_datos_json(data):
    archivo_base = id_paciente or "ANON_01"
    archivo = os.path.join(n_path,'results', f"{archivo_base}_NBack.json")
    registros = []

    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                registros = json.load(f)
            except json.JSONDecodeError:
                registros = []

    registros.append(data)

    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)


def generar_secuencia(n):
    seq = []
    for i in range(TRIALS):
        if i >= n and random.random() < 0.25:
            seq.append(seq[i - n])
        else:
            seq.append(random.randint(1, 5))
    return seq


def texto_instruccion_nivel(n):
    if n == 1:
        referencia = "la ronda anterior"
    else:
        referencia = f"hace {n} rondas"

    return (
        "Se le van a mostrar numeros durante 1 segundo\n"
        f"Debe indicar en 3 segundos si es el mismo numero que vio {referencia} utilizando los siguientes botones:\n"
    )


def iniciar_nivel():
    global secuencia, ronda, aciertos, errores, tiempos

    limpiar_temporizadores()
    boton_continuar.pack_forget()
    boton_salir.pack_forget()

    frame_botones.pack(pady=10)
    boton_si.pack(side="left", padx=10)
    boton_no.pack(side="right", padx=10)

    n = NIVELES[nivel_actual]
    secuencia = generar_secuencia(n)
    ronda = 0
    aciertos = 0
    errores = 0
    tiempos = []

    label_info.config(text=f"{n}-Back | ID: {id_paciente or 'N/D'}")
    label_estado.config(text=f"Nivel {n}-Back")
    label_numero.config(text="")
    label_pregunta.config(text=texto_instruccion_nivel(n))
    boton_si.config(state="disabled")
    boton_no.config(state="disabled")
    boton_continuar.config(text="Comenzar", state="normal")
    boton_continuar.pack(pady=20)


def comenzar_nivel():
    boton_continuar.pack_forget()
    siguiente_ronda()


def siguiente_ronda():
    global ronda, esperando_respuesta, ronda_token

    limpiar_temporizadores()

    if ronda >= TRIALS:
        mostrar_resultados()
        return

    ronda_token += 1
    num = secuencia[ronda]
    token_actual = ronda_token

    label_numero.config(text=str(num))
    label_estado.config(text=f"Ronda {ronda + 1}/{TRIALS}")
    label_pregunta.config(text="")
    boton_si.config(state="disabled")
    boton_no.config(state="disabled")
    esperando_respuesta = False

    programar_callback("after_ocultar", TIEMPO_ESTIMULO, lambda: ocultar_numero(token_actual))


def ocultar_numero(token):
    global inicio, esperando_respuesta, after_ocultar

    if token != ronda_token:
        return

    after_ocultar = None
    label_numero.config(text="")

    n = NIVELES[nivel_actual]
    if ronda >= n:
        label_pregunta.config(text=f"Coincide con hace {n} ronda{'s' if n > 1 else ''}?")
        boton_si.config(state="normal")
        boton_no.config(state="normal")
        inicio = time.perf_counter()
        esperando_respuesta = True
        programar_callback("after_timeout", TIEMPO_RESPUESTA, lambda: timeout(token))
    else:
        label_pregunta.config(text="...")
        programar_callback("after_avanzar", TIEMPO_FEEDBACK, lambda: avanzar(token))


def responder(resp):
    global aciertos, errores, tiempos, esperando_respuesta

    if not esperando_respuesta:
        return

    esperando_respuesta = False
    cancelar_temporizador("after_timeout")

    fin = time.perf_counter()
    tiempos.append(fin - inicio)

    n = NIVELES[nivel_actual]
    es_match = secuencia[ronda] == secuencia[ronda - n]

    if (resp == "si" and es_match) or (resp == "no" and not es_match):
        aciertos += 1
        label_pregunta.config(text="Correcto")
    else:
        errores += 1
        label_pregunta.config(text="Incorrecto")

    boton_si.config(state="disabled")
    boton_no.config(state="disabled")
    token_actual = ronda_token
    programar_callback("after_avanzar", TIEMPO_FEEDBACK, lambda: avanzar(token_actual))


def timeout(token):
    global errores, esperando_respuesta, after_timeout

    if token != ronda_token:
        return

    after_timeout = None
    if esperando_respuesta:
        esperando_respuesta = False
        errores += 1
        label_pregunta.config(text="Tiempo agotado")
        boton_si.config(state="disabled")
        boton_no.config(state="disabled")
        programar_callback("after_avanzar", TIEMPO_FEEDBACK, lambda: avanzar(token))


def avanzar(token=None):
    global ronda

    if token is not None and token != ronda_token:
        return

    limpiar_temporizadores()
    ronda += 1
    siguiente_ronda()


def mostrar_resultados():
    global nivel_actual

    limpiar_temporizadores()
    label_numero.config(text="")
    label_pregunta.config(text="NIVEL COMPLETADO")

    total = aciertos + errores
    acc = (aciertos / total) * 100 if total > 0 else 0
    tprom = sum(tiempos) / len(tiempos) if tiempos else 0

    datos_ronda = {
        "fecha": time.strftime("%Y-%m-%d %H:%M:%S"),
        "id_paciente": id_paciente,
        "edad": edad_paciente,
        "n_back": NIVELES[nivel_actual],
        "aciertos": aciertos,
        "errores": errores,
        "precision_pct": round(acc, 2),
        "tiempo_promedio_seg": round(tprom, 3),
    }
    guardar_datos_json(datos_ronda)

    label_estado.config(
        text=(
            f"Resultados Nivel {NIVELES[nivel_actual]}-Back:\n"
            f"Aciertos: {aciertos} | Errores: {errores}\n"
            f"Precision: {acc:.1f}%\n"
            f"Tiempo prom: {tprom:.2f}s"
        )
    )

    frame_botones.pack_forget()
    nivel_actual += 1

    boton_continuar.pack(side="left", padx=20, pady=20)
    boton_salir.pack(side="right", padx=20, pady=20)

    if nivel_actual < len(NIVELES):
        boton_continuar.config(text=f"Nivel {nivel_actual + 1}", state="normal")
    else:
        boton_salir.config(text="Finalizar", state="normal")
        boton_continuar.pack_forget()


def siguiente_nivel():
    boton_continuar.config(state="disabled")

    if nivel_actual >= len(NIVELES):
        root.quit()
    elif boton_continuar.cget("text") == "Comenzar":
        comenzar_nivel()
    else:
        iniciar_nivel()


root = tk.Tk()
root.title("N-Back PRO")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
root.configure(bg="white")

style = ttk.Style(root)
style.theme_use("clam")
style.configure(
    "Primary.TButton",
    font=("Arial", 20, "bold"),
    foreground="white",
    background="#4A90E2",
    borderwidth=0,
    padding=(18, 14),
)
style.map(
    "Primary.TButton",
    background=[("active", "#357ABD"), ("pressed", "#357ABD")],
    foreground=[("disabled", "#DCE8F8")],
)
style.configure(
    "Nav.TButton",
    font=("Arial", 24, "bold"),
    foreground="white",
    background="#4A90E2",
    borderwidth=0,
    padding=(10, 10),
)
style.map(
    "Nav.TButton",
    background=[("active", "#357ABD"), ("pressed", "#357ABD")],
    foreground=[("disabled", "#DCE8F8")],
)

top_bar = tk.Frame(root, bg="white", height=110)
top_bar.pack(side="top", fill="x")
top_bar.pack_propagate(False)

boton_volver = ttk.Button(
    top_bar,
    text="←",
    style="Nav.TButton",
    command=root.destroy,
)
boton_volver.place(x=20, y=15, width=90, height=90)

boton_cerrar = ttk.Button(
    top_bar,
    text="✕",
    style="Nav.TButton",
    command=cerrar_aplicacion_completa,
)
boton_cerrar.place(relx=1.0, x=-110, y=15, width=90, height=90)
root.protocol("WM_DELETE_WINDOW", cerrar_aplicacion_completa)

frame_test = tk.Frame(root, bg="white")
frame_test.pack()

label_info = tk.Label(frame_test, text="N-Back", font=("Arial", 26), bg="white")
label_info.pack(pady=10)

label_numero = tk.Label(frame_test, text="", font=("Arial", 60), bg="white")
label_numero.pack(pady=30)

label_estado = tk.Label(frame_test, text="", font=("Arial", 14), bg="white")
label_estado.pack()

label_pregunta = tk.Label(frame_test, text="", font=("Arial", 20), wraplength=700, justify="center", bg="white")
label_pregunta.pack(pady=10)

frame_botones = tk.Frame(frame_test, bg="white")
frame_botones.pack(pady=10)

boton_si = ttk.Button(
    frame_botones,
    text="Si",
    style="Primary.TButton",
    width=10,
    state="disabled",
    command=lambda: responder("si"),
)
boton_si.pack(side="left", padx=10)

boton_no = ttk.Button(
    frame_botones,
    text="No",
    style="Primary.TButton",
    width=10,
    state="disabled",
    command=lambda: responder("no"),
)
boton_no.pack(side="right", pady=10)

boton_continuar = ttk.Button(
    frame_test,
    text="Continuar",
    style="Primary.TButton",
    width=12,
    command=siguiente_nivel,
)

boton_salir = ttk.Button(
    frame_test,
    text="Salir",
    style="Primary.TButton",
    width=12,
    command=root.destroy,
)

iniciar_nivel()

root.mainloop()
