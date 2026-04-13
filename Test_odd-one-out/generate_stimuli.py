"""
generate_stimuli.py
Genera las imágenes de estímulos para el Test de Intruso Lógico (Odd-One-Out).
Usa emojis de color (NotoColorEmoji) en lugar de texto o figuras geométricas.
Ejecutar una sola vez antes de lanzar el test principal.
"""

import os
from PIL import Image, ImageDraw, ImageFont

# Ruta base del script (funciona sin importar desde qué carpeta se ejecute)
BASE_DIR    = os.path.dirname(os.path.abspath(__file__))
STIMULI_DIR = os.path.join(BASE_DIR, "assets", "stimuli")
IMG_SIZE    = (220, 220)
BG_COLOR    = (255, 255, 255, 255)
# Fuente incluida en el repositorio: funciona en Windows, macOS y Linux
EMOJI_FONT  = os.path.join(BASE_DIR, "assets", "NotoColorEmoji.ttf")
EMOJI_SIZE  = 109   # NotoColorEmoji renders at fixed 109px grid

os.makedirs(STIMULI_DIR, exist_ok=True)


def make_emoji_img(emoji: str) -> Image.Image:
    """Crea una imagen blanca cuadrada con el emoji centrado."""
    font = ImageFont.truetype(EMOJI_FONT, EMOJI_SIZE)
    img  = Image.new("RGBA", IMG_SIZE, BG_COLOR)
    d    = ImageDraw.Draw(img)

    # Medir tamaño real del glifo para centrarlo
    bbox = d.textbbox((0, 0), emoji, font=font, embedded_color=True)
    w = bbox[2] - bbox[0]
    h = bbox[3] - bbox[1]
    x = (IMG_SIZE[0] - w) // 2 - bbox[0]
    y = (IMG_SIZE[1] - h) // 2 - bbox[1]

    d.text((x, y), emoji, font=font, embedded_color=True)
    return img.convert("RGB")


def save(img: Image.Image, name: str):
    path = os.path.join(STIMULI_DIR, name)
    img.save(path)
    print(f"  Guardado: {path}")


# ─────────────────────────────────────────────────────────
# DEFINICIÓN DE ÍTEMS
# Cada ítem: lista de 4 emojis.
# Los primeros 3 son del mismo grupo; el ÚLTIMO (índice 3) es el intruso.
# ─────────────────────────────────────────────────────────

items = [
    # 0 – Frutas vs. vegetal
    ["🍎", "🍊", "🍇", "🥕"], 

    # 1 – En el cielo vs. en la tierra
    ["🪐", "⭐", "🌕", "🌲"],

    # 2 – Animales terrestres vs. pez
    ["🐶", "🐒", "🐘", "🦈"],

    # 3 – Instrumentos de cuerda vs. percusión
    ["🎻", "🎸", "🪉", "🥁"],

    # 4 – Transporte terrestre vs. aéreo
    ["🚗", "🚌", "🚲", "🚀"],

    # 5 – Ropa vs. accesorio
    ["🧥", "👖", "👕", "👓"],

    # 6 – Deportes con pelota vs. natación
    ["⚽", "🏀", "🎾", "🏊"],

    # 7 – Herramientas vs. tijera
    ["🔨", "🪛", "🔧", "🔐"],

    # 8 – Flores vs. árbol
    ["🌹", "🌻", "🌷", "🌳"],

    # 9 – Animales del mar vs. pájaro
    ["🐬", "🦈", "🐙", "🐦"],

    # 10 – Comidas dulces vs. pizza
    ["🍰", "🍫", "🍩", "🍕"],

    # 11 – Insectos vs. animal
    ["🐛", "🪰", "🦋", "🐹"],

    # 12 – Transporte acuático vs. auto
    ["🚢", "⛵", "🛶", "🚗"],

    # 13 – Animales de granja vs. pingüino
    ["🐄", "🐷", "🐔", "🐧"],

    # 14 – Bebidas vs. comida
    ["🍸", "☕", "🍺", "🍔"],
]

# ─────────────────────────────────────────────────────────
# GENERACIÓN
# ─────────────────────────────────────────────────────────
print(f"Generando {len(items)} ítems ({len(items) * 4} imágenes)...\n")

for i, emojis in enumerate(items):
    assert len(emojis) == 4, f"Ítem {i} debe tener exactamente 4 emojis"
    for j, emoji in enumerate(emojis):
        img = make_emoji_img(emoji)
        save(img, f"item{i:02d}_img{j}.png")

print(f"\n✅ Listo. Imágenes guardadas en '{STIMULI_DIR}/'")
