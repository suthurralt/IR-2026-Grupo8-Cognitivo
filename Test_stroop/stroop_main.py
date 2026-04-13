import time
import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from numpy import random
import os
import json
import csv
import sys
import signal
import pygame
import tkinter as tk

PRIMARY_BLUE = "#4A90E2"
PRIMARY_BLUE_HOVER = "#357ABD"

#Variables utiles 
colores = {'ROJO':'#ff1100', 'AZUL':'#0044ff', 'VERDE':'#00ff1e', 'AMARILLO':"#fadf0e"}
tecla_colores = dict(zip(['1','2','3','4'], colores.values()))
tecla_palabras= dict(zip(['1','2','3','4'],colores.keys()))
duracion_test=45
nPath = os.path.abspath(os.path.dirname(__file__))
pygame.mixer.init()

#sonidos
correcto =pygame.mixer.Sound(os.path.join(nPath,'resources_stroop','correcto.wav'))
incorrecto = pygame.mixer.Sound(os.path.join(nPath,'resources_stroop','incorrecto.wav'))
timer = pygame.mixer.Sound(os.path.join(nPath,'resources_stroop','timer.wav'))


def obtener_datos_paciente():
    patient_id = sys.argv[1].strip() if len(sys.argv) > 1 else None
    if not patient_id:
        return None, None

    csv_path = os.path.join(os.path.abspath(os.path.dirname(nPath)), "pacientes.csv")
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
                return patient_id, int(edad) if edad and edad.isdigit() else None

    return patient_id, None


def obtener_parent_pid():
    if len(sys.argv) > 2:
        try:
            return int(sys.argv[2])
        except ValueError:
            return None
    return None


ID_PACIENTE, EDAD_PACIENTE = obtener_datos_paciente()
PARENT_PID = obtener_parent_pid()


def cerrar_aplicacion_completa(root):
    if PARENT_PID is not None:
        try:
            os.kill(PARENT_PID, signal.SIGTERM)
        except OSError:
            pass
    root.destroy()

#funcion crea archivo o modifica el ya existente con los datos del test
def crear_file(id, edad, fecha, resultados, calificados):
    datos = {'id_paciente':id, 'fecha':fecha, 'módulo':'cognición y lenguaje', 'test':'stroop','edad':edad,'resultados':{'palabra':[resultados[0],calificados[0]], 'color':[resultados[1],calificados[1]], 'palabra-color':[resultados[2],calificados[2]],'índice interferencia':[resultados[3],calificados[3]]}}
    archivo= os.path.join(nPath, 'results', f'{id}_stroop.json')
    registros=[]
    if os.path.exists(archivo):
        with open(archivo, "r", encoding="utf-8") as f:
            try:
                registros = json.load(f)
            except json.JSONDecodeError:
                registros = []

    registros.append(datos)
    with open(archivo,'w', encoding='utf-8') as f:
        json.dump(registros, f, indent=4, ensure_ascii=False)

#funcion que corrige el puntaje por edad
def corregir_puntaje(edad,p,c,pc):
    if edad==7:
        return p+52, c+40,pc+26
    elif edad==8:
        return p+46,c+36,pc+24
    elif edad==9:
        return p+41,c+29,pc+20
    elif edad==10:
        return p+34,c+24,pc+16
    elif edad==11:
        return p+26,c+16,pc+11
    elif edad==12:
        return p+15,c+10,pc+7
    elif edad==13:
        return p+10,c+7,pc+5
    elif edad==14:
        return p+5,c,pc+2
    elif edad==15:
        return p+3,c,pc
    elif edad>=16 and edad<=44:
        return p,c,pc
    elif edad>=45 and edad<=64:
        return p+8,c+4,pc+5
    elif edad>=65 and edad<=80:
        return p+14,c+11,pc+15
#Corrige el puntaje de la modalidad manual a una vocal
def corregir_manual(p):
    return p+30
#funcion que califica los valores obtenidos
def calificar(p,c,pc,i):
    
    if p>=140:
        P='ALTO'
    elif p<140 and p>=76:
        P='NORMAL'
    else:
        P='BAJO'
    
    if c>=104:
        C='ALTO'
    elif c<104 and c>=56:
        C='NORMAL'
    else:
        C='BAJO'
    
    if pc>=61:
        PC='ALTO'
    elif pc<61 and pc>=29:
        PC='NORMAL'
    else:
        PC='BAJO'    
    
    
    if i>=16:
        I='ALTO'
    elif i<16 and i>=-16:
        I='NORMAL'
    else:
        I='bBAJOo'

    return [P,C,PC,I]


#Creacion ventana basica
def crear_ventana():
    root = ttk.Window(themename='litera', title='Test Stroop', size=(1200,600))

    root.attributes("-fullscreen", True)
    root.bind("<Escape>", lambda event: root.attributes("-fullscreen", False))

    style = ttk.Style()
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

    boton_salir = ttk.Button(
        top_bar,
        text="✕",
        style="Nav.TButton",
        command=lambda: cerrar_aplicacion_completa(root),
    )
    boton_salir.place(relx=1.0, x=-110, y=15, width=90, height=90)
    root.protocol("WM_DELETE_WINDOW", lambda: cerrar_aplicacion_completa(root))

    #Frame contenedor
    frame=ttk.Frame(root, padding=20)
    frame.pack(fill='both',expand=True)
   
    #configuraciones del grid para más adelante
    frame.rowconfigure(0,weight=9)
    frame.columnconfigure(0,weight=1)
    frame.columnconfigure(1,weight=0)
    
    return root,frame

#Funcion limpia frame
def clear(frame):
    for widget in frame.winfo_children():
        widget.destroy()

#Registro de datos
def inicio(root,frame):
    
    #creo el evento de presionar enter
    var = ttk.BooleanVar(value=False)
    def enter(event):
        var.set(True)

    root.bind("<Return>", enter)
    
    #Creo el Menu de inicio
    ttk.Label(frame, text='Test Stroop',font=("Arial",100, 'bold'),anchor=CENTER,background="#f8fcff").pack(expand=True, fill=BOTH,anchor=CENTER, side='top')
    ttk.Label(frame, text='Presiona ENTER para comenzar',font=("Arial",30),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='top')
    
    var.set(False)
    root.wait_variable(var)
    
    
    clear(frame)
    root.unbind('<Return>')
    
    return ID_PACIENTE, EDAD_PACIENTE
 
    
#Primera tarea: leer los colores
def tarea1(root,frame):
    
    #creo el evento de presionar enter
    var = ttk.BooleanVar(value=False)
    def enter(event):
        var.set(True)

    root.bind("<Return>", enter)
    
    #limpio la ventana por si quedo algo
    clear(frame)
    #frames organizativos
    frame_titulo=ttk.Frame(frame, padding=20)
    frame_titulo.pack(fill=BOTH,expand=True)
    frame_desc=ttk.Frame(frame)
    frame_desc.pack(fill=BOTH,expand=True)
    #Muestro las instrucciones
    ttk.Label(frame_titulo, text='PARTE I',font=("Arial",70, 'bold'),anchor=CENTER, background="#c1e2fa").pack(expand=True, fill=BOTH,anchor=CENTER, side='top')
    ttk.Label(frame_desc, text=f'DURACIÓN: {duracion_test}s',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    ttk.Label(frame_desc, text='TAREA: Leer las palabras que se muestran',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    ttk.Label(frame_desc, text='y presionar las teclas correctas',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER)
    ttk.Label(frame_desc, text='Presione ENTER para continuar',font=("Arial",20, 'italic'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    frame_codigo=ttk.Frame(frame_desc)
    frame_codigo.pack(expand=True, fill=BOTH,anchor=CENTER)
    for i in tecla_palabras.keys():
        ttk.Label(frame_codigo, text=f'[{i}]={tecla_palabras[i]}',font=("Arial",30,'bold'),foreground=tecla_colores[i],anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='left')
    #Espero a que presione enter
    var.set(False)
    root.wait_variable(var)
    
    #limpio la ventana desligo el evento enter
    clear(frame)
    root.unbind('<Return>')
    #defino variables útiles
    
    lista = list(colores.keys())
    valor=None
    resultado=0
    #creo el evento de presionar cualquier tecla
    root.unbind("<Key>")
    respuesta={'tecla':None}
    
    def tecla(event):
        if event.keysym.lower() in tecla_colores.keys():
            var.set(True)
            respuesta['tecla'] = event.keysym.lower()
    
    root.bind("<Key>", tecla)
#Doy tres segundos para prepararse 
    for i in range(3,0,-1):
        ttk.Label(frame, text=str(i),font=("Arial",150, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER)
        root.update()
        root.update_idletasks()
        timer.play(maxtime=200)
        time.sleep(1)
        clear(frame)
        
    clear(frame)    
    
    t_inicio = time.time()
    #Bucle de ejecución del test
    while time.time() - t_inicio <= duracion_test:
        
        
        #Muestra el nombre de un color en grande
        c=random.choice(lista)
        if valor != None:
            lista.append(valor)
        valor=c
        lista.remove(c)
        
        ttk.Label(frame, text=c,font=("Arial",80, 'bold'), anchor=CENTER, justify=CENTER).grid(row=0, column=0,sticky='nsew')
        frame_codigo=ttk.Frame(frame)
        frame_codigo.grid(row=1,column=0, sticky='nsew')
        for i in tecla_palabras.keys():
            ttk.Label(frame_codigo, text=f'[{i}]={tecla_palabras[i]}',font=("Arial",30,'bold'),foreground=tecla_colores[i],anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='left')
        
        #Si la leyó bien, entonces le suma un punto. No pasa hasta que ingrese el color correcto
        while True:
            root.update()
            var.set(False)
            root.wait_variable(var)
            if c == tecla_palabras[respuesta['tecla']]:     
                correcto.play(maxtime=200)
                resultado+=1
                break
            else:
                incorrecto.play(maxtime=300)
                pass

        #Limpia el frame de las palabras
        clear(frame)
    
    
    return resultado

#Segunda tarea:
def tarea2(root,frame):
    
    #creo el evento de presionar enter
    var = ttk.BooleanVar(value=False)
    def enter(event):
        var.set(True)

    root.bind("<Return>", enter)
    
    
    #limpio la ventana por si quedó algo
    clear(frame)
    #frames organizativos
    frame_titulo=ttk.Frame(frame, padding=20)
    frame_titulo.pack(fill=BOTH,expand=True)
    frame_desc=ttk.Frame(frame)
    frame_desc.pack(fill=BOTH,expand=True)
    #Muestro las instrucciones
    ttk.Label(frame_titulo, text='PARTE 2',font=("Arial",70, 'bold'),anchor=CENTER, background="#c1e2fa").pack(expand=True, fill=BOTH,anchor=CENTER, side='top')
    ttk.Label(frame_desc, text=f'DURACIÓN: {duracion_test}s',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    ttk.Label(frame_desc, text='TAREA: Identificar los colores que se muestran',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    ttk.Label(frame_desc, text='y presionar las teclas correctas',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER)
    ttk.Label(frame_desc, text='Presione ENTER para continuar',font=("Arial",20, 'italic'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    frame_codigo=ttk.Frame(frame_desc)
    frame_codigo.pack(expand=True, fill=BOTH,anchor=CENTER)
    for i in tecla_palabras.keys():
        ttk.Label(frame_codigo, text=f'[{i}]={tecla_palabras[i]}',font=("Arial",30,'bold'),foreground=tecla_colores[i],anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='left')
    #Espero a que presione enter
    var.set(False)
    root.wait_variable(var)
    
    #Defino variables útiles y limpio la ventana
    clear(frame)
    root.unbind('<Return>')
    
    lista=list(tecla_colores.keys())
    valor=None
    resultado=0
    
    #evento rojo, azul, verde 
    root.unbind("<Key>")
    var= ttk.BooleanVar(value=False)
    respuesta={'tecla':None}
    
    def tecla(event):
        if event.keysym.lower() in tecla_colores.keys():
            var.set(True)
            respuesta['tecla'] = event.keysym.lower()
    
    root.bind("<Key>", tecla)
    
    #Doy tres segundos para prepararse 
    for i in range(3,0,-1):
        ttk.Label(frame, text=str(i),font=("Arial",150, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER)
        root.update()
        root.update_idletasks()
        timer.play(maxtime=200)
        time.sleep(1)
        clear(frame)
    
    #inicializo timer    
    t_inicio = time.time()
    #Bucle de ejecución del test
    while time.time() - t_inicio <= duracion_test:
        
        
        #Muestra una X con el color elegido
        c=random.choice(lista)
        if valor != None:
            lista.append(valor)
        valor=c
        lista.remove(c)
        
        ttk.Label(frame, background=tecla_colores[c], font=("Arial",150, 'bold'), anchor=CENTER, justify=CENTER).grid(row=0, column=0,sticky='nsew')
        frame_codigo=ttk.Frame(frame)
        frame_codigo.grid(row=1,column=0, sticky='nsew')
        for i in tecla_palabras.keys():
            ttk.Label(frame_codigo, text=f'[{i}]={tecla_palabras[i]}',font=("Arial",30,'bold'),foreground=tecla_colores[i],anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='left')
        
        #Cuando ya ingresó el color, se fija si coincide con el que está mostrando y suma el puntaje
        while True:
            root.update()
            var.set(False)
            root.wait_variable(var)   
            
            if respuesta['tecla'] == c:
                correcto.play(maxtime=200)
                resultado+=1
                break
            else:
                incorrecto.play(maxtime=300)
                pass

        #Limpia el frame de su contenido
        for widget in frame.winfo_children():
            widget.destroy()
    
    return resultado

#Tercera tarea:
def tarea3(root,frame):
    #creo el evento de presionar enter
    var = ttk.BooleanVar(value=False)
    def enter(event):
        var.set(True)

    root.bind("<Return>", enter)
    #limpio la ventana por si quedo algo
    clear(frame)
    #frames organizativos
    frame_titulo=ttk.Frame(frame, padding=20)
    frame_titulo.pack(fill=BOTH,expand=True)
    frame_desc=ttk.Frame(frame)
    frame_desc.pack(fill=BOTH,expand=True)
    #Muestro las instrucciones
    ttk.Label(frame_titulo, text='PARTE 3',font=("Arial",70, 'bold'),anchor=CENTER, background="#c1e2fa").pack(expand=True, fill=BOTH,anchor=CENTER, side='top')
    ttk.Label(frame_desc, text=f'DURACIÓN: {duracion_test}s',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    ttk.Label(frame_desc, text=f'TAREA: Identificar el color de la tinta de la palabra',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    ttk.Label(frame_desc, text='y presionar las teclas correctas',font=("Arial",30, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER)
    ttk.Label(frame_desc, text='Presione ENTER para continuar',font=("Arial",20, 'italic'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, padx=5)
    frame_codigo=ttk.Frame(frame_desc)
    frame_codigo.pack(expand=True, fill=BOTH,anchor=CENTER)
    for i in tecla_palabras.keys():
        ttk.Label(frame_codigo, text=f'[{i}]={tecla_palabras[i]}',font=("Arial",30,'bold'),foreground=tecla_colores[i],anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='left')
    #Espero a que presione enter
    var.set(False)
    root.wait_variable(var)

    #limpio la ventana por si quedo algo
    clear(frame)
    root.unbind('<Return>')
    
    resultado=0
    teclas=list(tecla_colores.keys())
    lista = dict(zip(teclas, colores.keys()))
    valor_falso=None
    valor_real=None
    
    #evento rojo, azul, verde...
    root.unbind("<Key>")
    var= ttk.BooleanVar(value=False)
    respuesta={'tecla':None}
    
    def tecla(event):
        if event.keysym.lower() in tecla_colores.keys():
            var.set(True)
            respuesta['tecla'] = event.keysym.lower()
    
    root.bind("<Key>", tecla)
    
    #Doy tres segundos para prepararse 
    for i in range(3,0,-1):
        ttk.Label(frame, text=str(i),font=("Arial",150, 'bold'),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER)
        root.update()
        root.update_idletasks()
        timer.play(maxtime=200)
        time.sleep(1)
        clear(frame)
    
    #inicializo timer
    t_inicio = time.time()
    #Bucle de ejecución del test
    while time.time() - t_inicio <= duracion_test:
        
        if valor_falso == None:
            c_falso=random.choice(teclas)
            valor_falso=c_falso
            teclas.remove(c_falso)
            c_real=random.choice(teclas)
            valor_real=c_real
            teclas.remove(c_real)
        else:
            
            c_falso=random.choice(teclas)
            teclas.remove(c_falso)
            teclas.append(valor_falso)
            valor_falso=c_falso
            c_real=random.choice(teclas)
            teclas.remove(c_real)
            teclas.append(valor_real)
            valor_real=c_real
        
        ttk.Label(frame, text=lista[c_falso], foreground=colores[lista[c_real]], font=("Arial",80, 'bold'), anchor=CENTER, justify=CENTER).grid(row=0, column=0,sticky='nsew')
        frame_codigo=ttk.Frame(frame)
        frame_codigo.grid(row=1,column=0, sticky='nsew')
        for i in tecla_palabras.keys():
            ttk.Label(frame_codigo, text=f'[{i}]={tecla_palabras[i]}',font=("Arial",30,'bold'),foreground=tecla_colores[i],anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='left')
        #Cuando ya ingresó el color, se fija si coincide con el que está mostrando y suma el puntaje
        while True:
            root.update() 
            var.set(False)
            root.wait_variable(var)   
            if respuesta['tecla'] == c_real:
                correcto.play(maxtime=200)
                resultado+=1
                break
            else:
                incorrecto.play(maxtime=300)
                pass

        #Limpia el frame de su contenido
        
        clear(frame)
    
    
    return resultado

def pantalla_final(root, frame, resultados, calificaciones):
    #creo el evento de presionar enter
    var = ttk.BooleanVar(value=False)
    def enter(event):
        var.set(True)

    root.bind("<Return>", enter)
    
    #Creo el menu final

    ttk.Label(frame, text='RESULTADOS',font=("Arial",100, 'bold'),anchor=CENTER,background="#c1e2fa").pack(expand=True, fill=BOTH,anchor=CENTER, side='top')
    ttk.Label(frame, text=f'Condición Palabra: {calificaciones[0]} [{resultados[0]}]',font=("Arial",40),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='top',pady=5)
    ttk.Label(frame, text=f'Condición Color: {calificaciones[1]} [{resultados[1]}]',font=("Arial",40),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='top',pady=5)
    ttk.Label(frame, text=f'Condición Palabra-Color: {calificaciones[2]} [{resultados[2]}]',font=("Arial",40),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='top',pady=5)
    ttk.Label(frame, text=f'Índice de interferencia: {calificaciones[3]} [{resultados[3]}]',font=("Arial",40),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='top',pady=5)
    ttk.Label(frame, text='Presione ENTER para salir',font=("Arial",20,'italic' ),anchor=CENTER).pack(expand=True, fill=BOTH,anchor=CENTER, side='top',pady=20)
    var.set(False)
    root.wait_variable(var)

def main():
    root, frame = crear_ventana()
    id, edad = inicio(root,frame)

    if not id or edad is None:
        clear(frame)
        ttk.Label(frame, text='No se pudieron cargar los datos del paciente.', font=("Arial", 40, 'bold'), anchor=CENTER).pack(expand=True, fill=BOTH)
        ttk.Label(frame, text='Presione ENTER para salir', font=("Arial", 20, 'italic'), anchor=CENTER).pack(expand=True, fill=BOTH)
        var = ttk.BooleanVar(value=False)
        root.bind("<Return>", lambda event: var.set(True))
        root.wait_variable(var)
        root.destroy()
        return

    p=tarea1(root,frame)
    c=tarea2(root,frame)
    pc=tarea3(root, frame)
    P,C,PC = corregir_puntaje(edad,p,c,pc)
    P=corregir_manual(P)
    #calculo índice de interferencia
    I=round(PC-((P*C)/(P+C)), 2)
    calificado=calificar(P,C,PC,I)
    resultados=[P,C,PC,I]
    #guardo fecha de realización del test
    fecha= time.strftime("%Y-%m-%d %H:%M:%S")
    #creo el JSON 
    crear_file(id,edad,fecha,resultados,calificado)
    pantalla_final(root,frame,resultados,calificado)
if __name__=='__main__':
    main()
