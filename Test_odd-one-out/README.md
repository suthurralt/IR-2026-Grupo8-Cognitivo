# Test de Intruso Lógico (Odd-One-Out)

## Qué mide el test

Evaluación del **razonamiento inductivo y la capacidad de categorización** mediante la identificación del elemento que no pertenece a un grupo de estímulos visuales. El paciente observa 4 imágenes y debe señalar cuál es el intruso lógico, lo que permite evaluar funciones cognitivas como atención, abstracción y pensamiento conceptual.

## Instalación

```bash
# 1. Clonar o descargar el repositorio
git clone https://github.com/tu-usuario/IR-2026-GrupoN-IntrusoLogico.git
cd IR-2026-GrupoN-IntrusoLogico

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Generar las imágenes de estímulos (solo la primera vez)
python generate_stimuli.py

# 4. Ejecutar el test
python main.py
```

> **Nota:** Se requiere Python 3.10+ con soporte de Tkinter (incluido por defecto en las instalaciones estándar de Python en Windows y macOS).

## Estructura del proyecto

```
├── main.py                  # Aplicación principal
├── generate_stimuli.py      # Generador de imágenes de estímulos
├── requirements.txt
├── assets/
│   └── stimuli/             # Imágenes generadas (item00_img0.png, etc.)
│   └── NotoColorEmoji.ttf   # Archivo para la fuente de las imagenes
└── resultados/              # JSONs guardados automáticamente
```

## Población

Dirigido a pacientes adultos en rehabilitación cognitiva post-ACV (Accidente Cerebrovascular). La interfaz está diseñada con botones grandes, alto contraste y mínimas distracciones para ser apropiada para personas con posibles déficits atencionales, visuales o motores secundarios al ACV.

## Resultados

Los resultados se guardan automáticamente en la carpeta `resultados/` en formato JSON con el nombre del paciente y la fecha/hora. El archivo incluye:

- Número de respuestas correctas
- Porcentaje de acierto
- Tiempo de respuesta por ítem (en ms)
- Detalle de cada respuesta

## Criterios de diseño para ACV

- Imágenes grandes (200×200 px), bien diferenciadas
- Botones con área amplia clicable
- Fondo claro con texto de alto contraste
- Sin elementos decorativos que distraigan
- Confirmación explícita antes de registrar la respuesta
- Los datos se guardan automáticamente al finalizar
