# ui/theme.py
from PIL import ImageFont
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
FONTS_DIR = BASE_DIR / "assets" / "fonts"

# список кандидатов: сначала свои, потом системные
FONT_CANDIDATES = [
    (FONTS_DIR / "DejaVuSans.ttf", FONTS_DIR / "DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
     "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
    ("/usr/share/fonts/truetype/freefont/FreeSans.ttf",
     "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"),
]

def load_fonts():
    for regular, bold in FONT_CANDIDATES:
        try:
            reg_path = str(regular)
            bold_path = str(bold)
            font_sm = ImageFont.truetype(reg_path, 14)
            font_md = ImageFont.truetype(bold_path, 18)
            font_lg = ImageFont.truetype(bold_path, 28)
            return font_sm, font_md, font_lg
        except Exception:
            continue

    # последний фолбэк
    d = ImageFont.load_default()
    return d, d, d

font_sm, font_md, font_lg = load_fonts()
