import time
import random
import json
import os
import csv
import sys
import signal
from datetime import datetime
import tkinter as tk
from tkinter import ttk

PRIMARY_BLUE = "#4A90E2"
PRIMARY_BLUE_HOVER = "#357ABD"
LIGHT_BG = "white"

# -----------------------------
# Variables
# -----------------------------
# Acá defino los estímulos del test:
# TMT-A usa solo números del 1 al 20
numeros_A = list(range(1, 21))

# TMT-B usa números del 1 al 10 y letras A-J
numeros_B = list(range(1, 11))
letras_B = [chr(i) for i in range(65, 75)]

# Tiempo máximo permitido por test (en segundos)
duracion_max = 300
# Path absoluto al file
n_path=os.path.abspath(os.path.dirname(__file__))
# Identificación del paciente (anonimizado) 
# ------------------------------------------------------------------------------------------------------------------------------------------------------------
#HAY QUE VER QUIZAS DE CAMBIAR ESTO, DEPENDE COMO SE HACE EL LOG IN!!!!!!!!
def obtener_id_paciente():
    if len(sys.argv) < 2:
        return "ANON_01"

    patient_id = sys.argv[1].strip()
    csv_path = os.path.join(os.path.abspath(os.path.dirname(n_path)), "pacientes.csv")

    if not os.path.exists(csv_path):
        return patient_id or "ANON_01"

    with open(csv_path, mode="r", newline="", encoding="utf-8-sig") as file:
        reader = csv.DictReader(file)
        if reader.fieldnames:
            reader.fieldnames = [name.strip() for name in reader.fieldnames]

        for row in reader:
            clean_row = {k.strip(): (v.strip() if v is not None else "") for k, v in row.items() if k is not None}
            if clean_row.get("ID", "") == patient_id:
                return patient_id

    return patient_id or "ANON_01"


def obtener_parent_pid():
    if len(sys.argv) > 2:
        try:
            return int(sys.argv[2])
        except ValueError:
            return None
    return None


id_paciente = obtener_id_paciente()
parent_pid = obtener_parent_pid()


def cerrar_aplicacion_completa():
    if parent_pid is not None:
        try:
            os.kill(parent_pid, signal.SIGTERM)
        except OSError:
            pass
    root.destroy()
# ------------------------------------------------------------------------------------------------------------------------------------------------------------

# Nombre del módulo (sirve para el JSON)
modulo = "Cognitivo-TMT"

# Acá voy guardando todos los intentos del paciente
intentos = []

# -----------------------------
# Ventana
# -----------------------------
# Creo la ventana principal de la app
root = tk.Tk()
root.title('Trail Making Test Digital')
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))
root.configure(bg=LIGHT_BG)

style = ttk.Style(root)
style.theme_use("clam")
style.configure(
    "Action.TButton",
    font=("Arial", 20, "bold"),
    foreground="white",
    background=PRIMARY_BLUE,
    borderwidth=0,
    padding=(18, 14),
)
style.map(
    "Action.TButton",
    background=[("active", PRIMARY_BLUE_HOVER), ("pressed", PRIMARY_BLUE_HOVER)],
)
style.configure(
    "Nav.TButton",
    font=("Arial", 24, "bold"),
    foreground="white",
    background=PRIMARY_BLUE,
    borderwidth=0,
    padding=(10, 10),
)
style.map(
    "Nav.TButton",
    background=[("active", PRIMARY_BLUE_HOVER), ("pressed", PRIMARY_BLUE_HOVER)],
    foreground=[("disabled", "#DCE8F8")],
)
style.configure("Main.TFrame", background=LIGHT_BG)

top_bar = tk.Frame(root, bg=LIGHT_BG, height=110)
top_bar.pack(side="top", fill="x")
top_bar.pack_propagate(False)

boton_volver = ttk.Button(
    top_bar,
    text="←",
    style="Nav.TButton",
    command=root.destroy,
)
boton_volver.place(x=20, y=15, width=90, height=90)

boton_salir = ttk.Button(
    top_bar,
    text="✕",
    style="Nav.TButton",
    command=cerrar_aplicacion_completa,
)
boton_salir.place(relx=1.0, x=-110, y=15, width=90, height=90)
root.protocol("WM_DELETE_WINDOW", cerrar_aplicacion_completa)

# Frame contenedor donde voy a ir dibujando todo
frame = ttk.Frame(root, padding=50, style="Main.TFrame")
frame.pack(fill='both', expand=True)

# -----------------------------
def clear(frame):
    # Esta función la uso TODO el tiempo para limpiar la pantalla
    # borra todos los widgets del frame
    for widget in frame.winfo_children():
        widget.destroy()

# -----------------------------
def mostrar_instrucciones(texto):
    # Antes de cada test muestro instrucciones claras al paciente
    clear(frame)

    tk.Label(frame, text=texto, font=("Arial", 20),
             wraplength=700, justify="center", bg=LIGHT_BG).pack(expand=True)

    # Botón para arrancar el test
    ttk.Button(frame, text="Comenzar", style="Action.TButton", command=root.quit).pack(pady=20)

    # Espero a que el usuario toque "Comenzar"
    root.mainloop()

    # Limpio para pasar al test
    clear(frame)

# -----------------------------
def tmt_test(lista_objetivos, titulo, alternancia=False):

    # Armo las instrucciones dependiendo del tipo de test
    if alternancia:
        instrucciones = (
            f"{titulo}\n\n"
            "Haz click siguiendo:\n"
            "1 → A → 2 → B → 3 → C...\n\n"
            "Se mide tiempo y errores.\n"
            "Puedes rendirte."
        )
    else:
        instrucciones = (
            f"{titulo}\n\n"
            "Haz click en orden:\n"
            "1 → 2 → 3 → ... → 20\n\n"
            "Se mide tiempo y errores.\n"
            "Puedes rendirte."
        )

    # Muestro instrucciones antes de empezar
    mostrar_instrucciones(instrucciones)

    clear(frame)

    # Inicializo métricas del test
    errores = 0
    index_correcto = 0
    start = time.time()  # arranco a medir tiempo

    # Diccionario para controlar si el test terminó o si se rindió
    terminado = {'value': False, 'rendicion': False}

    # Mezclo los estímulos → clave del TMT
    lista_mostrar = lista_objetivos.copy()
    random.shuffle(lista_mostrar)

    # Armo la secuencia correcta que el usuario debería seguir
    if alternancia:
        # Para TMT-B alterno número-letra
        numeros_iter = iter(sorted(numeros_B))
        letras_iter = iter(sorted(letras_B))
        secuencia_correcta = []
        for i in range(len(lista_objetivos)):
            if i % 2 == 0:
                secuencia_correcta.append(next(numeros_iter))
            else:
                secuencia_correcta.append(next(letras_iter))
    else:
        # Para TMT-A es simplemente orden ascendente
        secuencia_correcta = sorted(lista_objetivos)

    def click_elemento(valor):
        # Esta función se ejecuta cada vez que el usuario hace click
        nonlocal index_correcto, errores

        # Si ya terminó, no hago nada
        if terminado['value']:
            return

        # Verifico si el click fue correcto
        if valor == secuencia_correcta[index_correcto]:
            index_correcto += 1

            # Marco en verde, deshabilito y simulo botón "apretado"
            btns[valor].config(bg='lightgreen', state='disabled', relief='sunken')
        else:
            errores += 1

            # Marco error en rojo
            btns[valor].config(bg='red')

    def rendirse():
        # Si el usuario abandona, lo registro
        terminado['value'] = True
        terminado['rendicion'] = True

    tablero = tk.Frame(frame, bg=LIGHT_BG)
    tablero.pack(expand=True)

    # Creo todos los botones del test
    btns = {}
    for i, val in enumerate(lista_mostrar):
        btn = tk.Button(tablero, text=str(val), width=4, height=1, font=("Arial", 22, "bold"),
                        command=lambda v=val: click_elemento(v))
        btn.grid(row=i//5, column=i%5, padx=10, pady=10)
        
        btns[val] = btn

    # Botón para rendirse
    ttk.Button(frame, text="Me rindo",
              style="Action.TButton", command=rendirse).pack(pady=18)

    # Loop principal del test
    # Se mantiene corriendo hasta que termine o se rinda
    while index_correcto < len(secuencia_correcta) and not terminado['value']:
        root.update()

        # También corto si se pasa del tiempo máximo
        if time.time() - start > duracion_max:
            break

    # Calculo tiempo total
    tiempo_total = round(time.time() - start, 2)

    # Devuelvo métricas del test
    return {
        "tiempo": tiempo_total,
        "errores": errores,
        "rendicion": terminado['rendicion']
    }

# -----------------------------
def generar_observacion(): #extra: comentarios automatizados
    # Genero una interpretación simple automática (tipo IA)
    if len(intentos) < 2:
        return "Datos insuficientes."

    ultimo = intentos[-1]

    # Si se rindió en TMT-B → posible fatiga o dificultad ejecutiva
    if ultimo["TMT_B"]["rendicion"]:
        return "Posible fatiga o dificultad en funciones ejecutivas."

    # Comparo errores entre A y B
    if ultimo["TMT_B"]["errores"] > ultimo["TMT_A"]["errores"]:
        return "Mayor dificultad en flexibilidad cognitiva."

    return "Rendimiento dentro de lo esperado."

# -----------------------------
def guardar_json():

    # Guardo el archivo en la misma carpeta del script
    ruta = os.path.join(n_path, 'results' ,f"{id_paciente}_tsecuencia.json")

    # Calculo promedio total (A + B)
    valor_promedio = sum(
        (i["TMT_A"]["tiempo"] + i["TMT_B"]["tiempo"])
        for i in intentos
    ) / len(intentos)

    # Estructura final del JSON
    data = {
        "id_paciente": id_paciente,
        "fecha": datetime.now().strftime("%Y-%m-%d"),
        "modulo": modulo,
        "metrica_principal": "Tiempo total",
        "valor_promedio": valor_promedio,
        "unidad": "s",
        "intentos": intentos,
        "observaciones_ia": generar_observacion()
    }

    # Escribo el archivo
    with open(ruta, "w") as f:
        json.dump(data, f, indent=4)

    print(f"Guardado en: {ruta}")

# -----------------------------
def main():

    seguir = True  # controlo si el usuario quiere repetir

    while seguir:

        # Corro ambos tests
        rA = tmt_test(numeros_A, "TMT-A")
        rB = tmt_test(numeros_B + letras_B, "TMT-B", alternancia=True)

        # Registro el intento separando A y B (clave clínicamente)
        intento = {
            "intento": len(intentos) + 1,
            "TMT_A": {
                "tiempo": rA["tiempo"],
                "errores": rA["errores"],
                "rendicion": rA["rendicion"]
            },
            "TMT_B": {
                "tiempo": rB["tiempo"],
                "errores": rB["errores"],
                "rendicion": rB["rendicion"]
            }
        }

        # Lo agrego a la lista de intentos
        intentos.append(intento)

        # También lo imprimo en consola
        print(intento)

        clear(frame)

        # Pantalla de fin de intento
        tk.Label(frame, text="Intento finalizado",
                  font=("Arial", 20), bg=LIGHT_BG).pack(pady=20)

        def otro():
            # Permite repetir sin cerrar la app
            nonlocal seguir
            seguir = True
            root.quit()

        def finalizar():
            # Guarda datos y cierra todo
            nonlocal seguir
            guardar_json()
            seguir = False
            root.destroy()

        ttk.Button(frame, text="Otro intento", style="Action.TButton", command=otro).pack(pady=10)
        ttk.Button(frame, text="Finalizar", style="Action.TButton", command=finalizar).pack(pady=10)

        root.mainloop()

# -----------------------------
if __name__ == "__main__":
    main()
