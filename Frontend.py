import tkinter as tk
from tkinter import ttk
import csv
import os
import subprocess
import sys

CSV_FILE = "pacientes.csv"
SEQUENCE_TEST_FILE = os.path.join('Test_secuencia',"tmt.py")
STROOP_TEST_FILE = os.path.join('Test_stroop',"stroop_main.py")
N_BACK_TEST_FILE = os.path.join('Test_n-back',"N_Back.py")
ODD_ONE_OUT_TEST_FILE = os.path.join("Test_odd-one-out", "odd_one_out.py")


def show_custom_message(parent, title, message, msg_type="info"):
    win = tk.Toplevel(parent)
    win.title(title)
    win.configure(bg="#EEF5FF")
    win.transient(parent)
    win.grab_set()
    win.resizable(False, False)

    w = 900
    h = 420
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw // 2) - (w // 2)
    y = (sh // 2) - (h // 2)
    win.geometry(f"{w}x{h}+{x}+{y}")

    title_font = ("Arial", 26, "bold")
    msg_font = ("Arial", 20)
    btn_font = ("Arial", 20, "bold")
    primary_blue = "#4A90E2"
    primary_blue_hover = "#357ABD"

    if msg_type == "error":
        symbol = "X"
        accent = "#D62828"
    elif msg_type == "warning":
        symbol = "!"
        accent = "#D97706"
    else:
        symbol = "i"
        accent = primary_blue

    container = tk.Frame(win, bg="#EEF5FF")
    container.pack(expand=True, fill="both", padx=28, pady=28)

    card = tk.Frame(
        container,
        bg="white",
        highlightthickness=1,
        highlightbackground="#D7E6FA",
        bd=0,
    )
    card.pack(expand=True, fill="both")

    header = tk.Frame(card, bg=primary_blue, height=78)
    header.pack(fill="x")
    header.pack_propagate(False)

    tk.Label(
        header,
        text=f"{symbol}  {title}",
        font=title_font,
        bg=primary_blue,
        fg="white",
    ).pack(expand=True)

    tk.Label(
        card,
        text=message,
        font=msg_font,
        bg="white",
        fg="#22324A",
        wraplength=760,
        justify="center",
    ).pack(pady=(48, 26), padx=35)

    tk.Button(
        card,
        text="Aceptar",
        font=btn_font,
        bg=primary_blue,
        fg="white",
        activebackground=primary_blue_hover,
        activeforeground="white",
        relief="flat",
        bd=0,
        command=win.destroy,
    ).pack(pady=(0, 34), ipadx=26, ipady=12)

    separator = tk.Frame(card, bg=accent, height=4)
    separator.pack(side="bottom", fill="x")

    win.wait_window()

def open_test(parent, name, patient_id):
    if name == "1. Test de la secuencia":
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), SEQUENCE_TEST_FILE)

        if not os.path.exists(test_path):
            show_custom_message(
                parent,
                "Archivo no encontrado",
                f"No se encontró el archivo:\n{SEQUENCE_TEST_FILE}",
                "error"
            )
            return

        try:
            subprocess.Popen([sys.executable, test_path, patient_id, str(os.getpid())])
        except Exception as error:
            show_custom_message(
                parent,
                "Error al abrir test",
                f"No se pudo ejecutar el test.\n\nDetalle: {error}",
                "error"
            )
        return

    if name == "3. Test N-back" and hasattr(parent, "show_nback_test"):
        parent.show_nback_test()
        return

    if name == "2. Test odd one out" and hasattr(parent, "show_odd_one_out_test"):
        parent.show_odd_one_out_test()
        return

    if name == "4. Test Stroop" and hasattr(parent, "show_stroop_test"):
        parent.show_stroop_test()
        return

    show_custom_message(
        parent,
        "Test",
        f"{name}\nPatient ID: {patient_id}\n(Not implemented)",
        "info"
    )


class App(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("Tests Cognitivos")
        self.configure(bg="white")
        self.attributes("-fullscreen", True)
        self.bind("<Escape>", lambda e: self.attributes("-fullscreen", False))

        self.title_font = ("Arial", 26, "bold")
        self.label_font = ("Arial", 22, "bold")
        self.entry_font = ("Arial", 20)
        self.button_font = ("Arial", 20, "bold")
        self.back_font = ("Arial", 36, "bold")
        self.close_font = ("Arial", 30, "bold")

        self.btn_bg = "#ADD8E6"
        self.btn_fg = "black"
        self.primary_blue = "#4A90E2"
        self.primary_blue_hover = "#357ABD"
        self.entry_bg = "#F7FAFF"

        self.current_patient_id = None
        self.current_patient_name = None
        self.previous_screen = None
        self.active_test_frame = None

        self.style = ttk.Style(self)
        self.style.theme_use("clam")
        self.configure_ttk_styles()

        self.ensure_csv_exists()

        # Barra superior fija
        self.top_bar = tk.Frame(self, bg="white", height=110)
        self.top_bar.pack(side="top", fill="x")
        self.top_bar.pack_propagate(False)

        self.back_button = ttk.Button(
            self.top_bar,
            text="←",
            style="Nav.TButton",
            command=self.go_back
        )
        self.back_button.place(x=20, y=15, width=90, height=90)

        self.close_button = ttk.Button(
            self.top_bar,
            text="✕",
            style="Nav.TButton",
            command=self.destroy
        )
        self.close_button.place(relx=1.0, x=-110, y=15, width=90, height=90)

        # Área central
        self.main_frame = tk.Frame(self, bg="white")
        self.main_frame.pack(expand=True, fill="both")

        self.show_home()

    def configure_ttk_styles(self):
        self.style.configure(
            "Primary.TButton",
            font=self.button_font,
            foreground="white",
            background=self.primary_blue,
            borderwidth=0,
            padding=(18, 14),
        )
        self.style.map(
            "Primary.TButton",
            background=[("active", self.primary_blue_hover), ("pressed", self.primary_blue_hover)],
            foreground=[("disabled", "#DCE8F8")],
        )

        self.style.configure(
            "Nav.TButton",
            font=("Arial", 24, "bold"),
            foreground="white",
            background=self.primary_blue,
            borderwidth=0,
            padding=(10, 10),
        )
        self.style.map(
            "Nav.TButton",
            background=[("active", self.primary_blue_hover), ("pressed", self.primary_blue_hover)],
            foreground=[("disabled", "#DCE8F8")],
        )

        self.style.configure(
            "Form.TEntry",
            font=self.entry_font,
            fieldbackground=self.entry_bg,
            foreground="black",
            bordercolor="#9BBCE4",
            lightcolor="#9BBCE4",
            darkcolor="#9BBCE4",
            padding=(10, 8),
        )

    def create_primary_button(self, parent, text, command, width=None):
        button = ttk.Button(parent, text=text, command=command, style="Primary.TButton")
        if width is not None:
            button.configure(width=width)
        return button

    def create_form_entry(self, parent):
        return ttk.Entry(parent, font=self.entry_font, justify="center", style="Form.TEntry")

    def ensure_csv_exists(self):
        if not os.path.exists(CSV_FILE):
            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Nombre", "Apellido", "Edad"])
            return

        with open(CSV_FILE, mode="r", newline="", encoding="utf-8-sig") as file:
            rows = list(csv.reader(file))

        if not rows:
            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(["ID", "Nombre", "Apellido", "Edad"])
            return

        header = [h.strip() for h in rows[0]]
        if "Edad" not in header:
            header.append("Edad")
            fixed_rows = [header]
            for row in rows[1:]:
                while len(row) < len(header):
                    row.append("")
                fixed_rows.append(row[:len(header)])

            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerows(fixed_rows)

    def clear_main(self):
        if self.active_test_frame is not None and hasattr(self.active_test_frame, "cleanup"):
            self.active_test_frame.cleanup()
            self.active_test_frame = None

        for widget in self.main_frame.winfo_children():
            widget.destroy()

    def set_back_enabled(self, enabled=True):
        if enabled:
            self.back_button.config(state="normal")
        else:
            self.back_button.config(state="disabled")

    def go_back(self):
        if self.previous_screen is not None:
            self.previous_screen()

    def get_patient_by_id(self, patient_id):
        if not os.path.exists(CSV_FILE):
            return None

        with open(CSV_FILE, mode="r", newline="", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            # Normaliza encabezados por si tienen espacios o BOM
            if reader.fieldnames:
                reader.fieldnames = [name.strip() for name in reader.fieldnames]

            for row in reader:
                # Normaliza también las claves y valores de cada fila
                clean_row = {k.strip(): v.strip() for k, v in row.items() if k is not None}

                if clean_row.get("ID", "") == patient_id.strip():
                    return clean_row

        return None

    def register_patient(self, patient_id, nombre, apellido, edad):
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow([patient_id.strip(), nombre.strip(), apellido.strip(), edad.strip()])

    def valid_id(self, patient_id):
        return patient_id.isdigit() and len(patient_id) == 8

    def show_home(self):
        self.previous_screen = None
        self.set_back_enabled(False)
        self.clear_main()

        center_frame = tk.Frame(self.main_frame, bg="white")
        center_frame.pack(expand=True)

        tk.Label(
            center_frame,
            text="Cognitive Tests",
            font=self.title_font,
            bg="white",
            fg="black"
        ).pack(pady=(0, 50))

        self.create_primary_button(center_frame, "Registrarse", self.show_register, width=18).pack(pady=18)

        self.create_primary_button(center_frame, "Ingresar", self.show_login, width=18).pack(pady=18)

    def show_register(self):
        self.previous_screen = self.show_home
        self.set_back_enabled(True)
        self.clear_main()

        form_frame = tk.Frame(self.main_frame, bg="white")
        form_frame.pack(expand=True)

        tk.Label(
            form_frame,
            text="Registro de paciente",
            font=self.title_font,
            bg="white",
            fg="black"
        ).pack(pady=(0, 30))

        fields_frame = tk.Frame(form_frame, bg="white")
        fields_frame.pack(pady=(8, 10))

        left_column = tk.Frame(fields_frame, bg="white")
        left_column.grid(row=0, column=0, padx=30)

        right_column = tk.Frame(fields_frame, bg="white")
        right_column.grid(row=0, column=1, padx=30)

        tk.Label(left_column, text="Nombre:", font=self.label_font, bg="white").pack(pady=(0, 6))
        self.register_name_entry = self.create_form_entry(left_column)
        self.register_name_entry.pack(ipady=6, ipadx=40)

        tk.Label(left_column, text="Apellido:", font=self.label_font, bg="white").pack(pady=(20, 6))
        self.register_lastname_entry = self.create_form_entry(left_column)
        self.register_lastname_entry.pack(ipady=6, ipadx=40)

        tk.Label(right_column, text="Edad:", font=self.label_font, bg="white").pack(pady=(0, 6))
        self.register_age_entry = self.create_form_entry(right_column)
        self.register_age_entry.pack(ipady=6, ipadx=40)

        tk.Label(right_column, text="ID (8 numeros):", font=self.label_font, bg="white").pack(pady=(20, 6))
        self.register_id_entry = self.create_form_entry(right_column)
        self.register_id_entry.pack(ipady=6, ipadx=40)

        self.create_primary_button(form_frame, "Guardar registro", self.on_register, width=20).pack(pady=20)

    def show_login(self):
        self.previous_screen = self.show_home
        self.set_back_enabled(True)
        self.clear_main()

        form_frame = tk.Frame(self.main_frame, bg="white")
        form_frame.pack(expand=True)

        tk.Label(
            form_frame,
            text="Ingreso de paciente",
            font=self.title_font,
            bg="white",
            fg="black"
        ).pack(pady=(0, 30))

        tk.Label(
            form_frame,
            text="Ingrese Patient ID:",
            font=self.label_font,
            bg="white"
        ).pack(pady=(8, 10))

        self.login_id_entry = self.create_form_entry(form_frame)
        self.login_id_entry.pack(ipady=8, ipadx=40)

        self.create_primary_button(form_frame, "Ingresar", self.on_login, width=18).pack(pady=30)

    def show_menu(self, patient_id, full_name):
        self.previous_screen = self.show_login
        self.set_back_enabled(True)
        self.clear_main()

        self.current_patient_id = patient_id
        self.current_patient_name = full_name

        tk.Label(
            self.main_frame,
            text=f"Bienvenido: {full_name}",
            font=self.title_font,
            bg="white",
            fg="black"
        ).pack(pady=(40, 10))

        tk.Label(
            self.main_frame,
            text=f"ID del paciente: {patient_id}",
            font=self.label_font,
            bg="white",
            fg="black"
        ).pack(pady=(0, 25))

        btns_frame = tk.Frame(self.main_frame, bg="white")
        btns_frame.pack(pady=20)

        tests = ["1. Test de la secuencia", "2. Test odd one out", "3. Test N-back", "4. Test Stroop"]

        for i, t in enumerate(tests):
            b = ttk.Button(
                btns_frame,
                text=t,
                style="Primary.TButton",
                width=24,
                command=lambda name=t: open_test(self, name, patient_id)
            )
            b.grid(row=i // 2, column=i % 2, padx=20, pady=20)

    def show_nback_test(self):
        self.previous_screen = lambda: self.show_menu(self.current_patient_id, self.current_patient_name)
        self.set_back_enabled(True)
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), N_BACK_TEST_FILE)

        if not os.path.exists(test_path):
            show_custom_message(
                self,
                "Archivo no encontrado",
                f"No se encontro el archivo:\n{N_BACK_TEST_FILE}",
                "error"
            )
            return

        try:
            subprocess.Popen([sys.executable, test_path, self.current_patient_id, str(os.getpid())])
        except Exception as error:
            show_custom_message(
                self,
                "Error al abrir test",
                f"No se pudo ejecutar el test N-Back.\n\nDetalle: {error}",
                "error"
            )

    def show_odd_one_out_test(self):
        self.previous_screen = lambda: self.show_menu(self.current_patient_id, self.current_patient_name)
        self.set_back_enabled(True)
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), ODD_ONE_OUT_TEST_FILE)

        if not os.path.exists(test_path):
            show_custom_message(
                self,
                "Archivo no encontrado",
                f"No se encontro el archivo:\n{ODD_ONE_OUT_TEST_FILE}",
                "error"
            )
            return

        try:
            subprocess.Popen([sys.executable, test_path, self.current_patient_id, str(os.getpid())])
        except Exception as error:
            show_custom_message(
                self,
                "Error al abrir test",
                f"No se pudo ejecutar el test Odd One Out.\n\nDetalle: {error}",
                "error"
            )

    def show_stroop_test(self):
        self.previous_screen = lambda: self.show_menu(self.current_patient_id, self.current_patient_name)
        self.set_back_enabled(True)
        test_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), STROOP_TEST_FILE)

        if not os.path.exists(test_path):
            show_custom_message(
                self,
                "Archivo no encontrado",
                f"No se encontro el archivo:\n{STROOP_TEST_FILE}",
                "error"
            )
            return

        try:
            subprocess.Popen([sys.executable, test_path, self.current_patient_id, str(os.getpid())])
        except Exception as error:
            show_custom_message(
                self,
                "Error al abrir test",
                f"No se pudo ejecutar el test Stroop.\n\nDetalle: {error}",
                "error"
            )

    def on_register(self):
        patient_id = self.register_id_entry.get().strip()
        nombre = self.register_name_entry.get().strip()
        apellido = self.register_lastname_entry.get().strip()
        edad = self.register_age_entry.get().strip()

        if not patient_id or not nombre or not apellido or not edad:
            show_custom_message(
                self,
                "Campos incompletos",
                "Por favor complete todos los campos.",
                "warning"
            )
            return

        if not self.valid_id(patient_id):
            show_custom_message(
                self,
                "ID inválido",
                "El ID debe tener exactamente 8 números.",
                "error"
            )
            return

        if self.get_patient_by_id(patient_id) is not None:
            show_custom_message(
                self,
                "ID existente",
                "Ese ID ya está registrado.",
                "error"
            )
            return

        self.register_patient(patient_id, nombre, apellido, edad)

        show_custom_message(
            self,
            "Registro exitoso",
            f"Paciente registrado:\n{nombre} {apellido}\nID: {patient_id}",
            "info"
        )
        self.show_home()

    def on_login(self):
        patient_id = self.login_id_entry.get().strip()

        if not patient_id:
            show_custom_message(
                self,
                "Falta ID",
                "Por favor ingrese el Patient ID.",
                "warning"
            )
            return

        patient = self.get_patient_by_id(patient_id)

        if patient is None:
            show_custom_message(
                self,
                "No está registrado",
                "No está registrado.",
                "error"
            )
            return

        nombre = patient.get("Nombre", "")
        apellido = patient.get("Apellido", "")
        full_name = f"{nombre} {apellido}".strip()

        show_custom_message(
            self,
            "Bienvenido",
            f"Bienvenido: {full_name}",
            "info"
        )

        self.show_menu(patient_id, full_name)


if __name__ == "__main__":
    app = App()
    app.mainloop()
