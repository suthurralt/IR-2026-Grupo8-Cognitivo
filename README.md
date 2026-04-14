# IR-2026-Grupo8-Cognitivo — Módulo de Cognición y Lenguaje

> Batería de tests neuropsicológicos digitales para la evaluación cognitiva de pacientes post-ACV, desarrollada como parte de la plataforma **OpenRehab ACV**.

---

## ¿Qué mide este módulo?

Este módulo evalúa cuatro dominios cognitivos frecuentemente afectados tras un Accidente Cerebrovascular (ACV):

| Test | Función evaluada | Métrica principal |
|------|-----------------|-------------------|
| **Stroop** | Control inhibitorio y velocidad de procesamiento | Índice de interferencia (score) |
| **N-Back** | Memoria de trabajo y atención sostenida | Porcentaje de aciertos por nivel |
| **TMT (Trail Making Test)** | Flexibilidad cognitiva y atención alternante | Tiempo de ejecución (segundos) |
| **Odd-One-Out** | Razonamiento categorial y percepción visual | Aciertos sobre total de intentos |

Todos los resultados se guardan automáticamente en formato **JSON** por paciente, incluso si el programa se cierra inesperadamente.

---

## Población objetivo

Dirigido a **pacientes adultos en etapa de rehabilitación post-ACV**, especialmente aquellos con:
- Déficits atencionales o de memoria de trabajo
- Alteraciones en velocidad de procesamiento
- Necesidad de evaluación con **una sola mano** (diseño accesible)
- Baja tolerancia a interfaces complejas o con muchos estímulos

La interfaz fue diseñada con **alto contraste**, botones de gran tamaño y sin necesidad de doble clic, siguiendo criterios de accesibilidad para este perfil clínico.

---

## Instalación

### Requisitos previos

- Python 3.10 o superior
- pip actualizado

### Pasos

```bash
# 1. Clonar el repositorio
git clone https://github.com/suthurralt/IR-2026-Grupo8-Cognitivo.git
cd IR-2026-Grupo8-Cognitivo

# 2. (Recomendado) Crear entorno virtual
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows

cd ~/IR-2026-Grupo8-Cognitivo


# 3. Instalar dependencias
pip install -r requirements.txt


# En mac puede ser
pip3 install -r requirements.txt

# 4. Ejecutar la aplicación
python Frontend.py

# En mac puede ser
python3 Frontend.py
```

> ⚠️ No mover los archivos de carpeta. El programa usa rutas relativas para encontrar los tests y recursos de audio.

---

## Estructura del proyecto

```
IR-2026-Grupo8-Cognitivo/
│
├── Frontend.py               # Punto de entrada — login y menú principal
├── Test_odd-one-out/         
|   ├── assets/
|   ├── resultados/
|   ├── generate_stimuli.py
|   └── odd_one_out.py       # Test Odd-One-Out     
|
├── Test_n-back
|   ├── results/
|   └── N_Back.py             # Test N-Back
|
├── Test_secuencia
|   ├── resultados/
|   └── tmt.py                # Trail Making Test (TMT-A y TMT-B)
│
├── Test_stroop/
│   ├── resources_stroop/
│   ├── results/
│   └── stroop_main.py        # Test de Stroop
│
├── pacientes.csv             # Registro de pacientes
├── requirements.txt
└── README.md
```

---

## Formato de salida (JSON)

Cada test genera un archivo JSON por paciente al finalizar (o si se interrumpe). Ejemplo del Test de Stroop:

```json
{
    "id_paciente": "12345678",
    "fecha": "07/04/2026",
    "módulo": "cognición y lenguaje",
    "test": "stroop",
    "edad": 79,
    "resultados": {
        "palabra": [26, "bajo"],
        "color": [62, "normal"],
        "palabra-color": [45, "normal"],
        "índice interferencia": [26.68, "alto"]
    }
}
```

Campos presentes en todos los tests: `id_paciente`, `fecha`, `test`, `métrica_principal`, `unidad`, `intentos`.

---

## Dependencias

Ver [`requirements.txt`](requirements.txt). Las principales son:

- `ttkbootstrap` — Estilizado moderno de interfaces Tkinter
- `pygame` — Reproducción de audio (feedback sonoro)
- `numpy` — Generación de estímulos aleatorios

---

## Robustez y guardado de datos

- Los resultados se **guardan automáticamente** al finalizar cada test y también ante cierre inesperado del programa (manejo de señales `SIGINT`/`SIGTERM`).
- Si el paciente cierra la ventana a mitad del test, el JSON se escribe igualmente con los datos parciales recolectados hasta ese momento.
- Los archivos JSON se nombran con el formato: `<id_paciente>_<test>.json`

---

## Criterios de diseño accesible

- ✅ Operable con **una sola mano** (teclado o mouse)
- ✅ **Alto contraste** (fondo claro, texto oscuro, azul primario `#4A90E2`)
- ✅ Botones de mínimo 60px de alto
- ✅ Sin doble clic requerido
- ✅ Sin animaciones distractoras
- ✅ Mensajes de error y confirmación en lenguaje claro

---

## Autores

Proyecto desarrollado para la cátedra de Ingeniería en Rehabilitación — 2026 - Grupo 8.
