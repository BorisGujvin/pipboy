# ui/theme.py
from PIL import ImageFont

PIP_BG = (16, 24, 16)
PIP_PANEL = (24, 40, 24)
PIP_ACCENT = (80, 200, 120)
PIP_TEXT = (180, 255, 200)
PIP_TEXT_DIM = (120, 180, 140)
TAB_BG = (10, 20, 10)
TAB_ACTIVE = (40, 90, 60)
DIV_LINE = (50, 90, 60)

TAB_H = 44
PADDING = 10

try:
    FONT_PATH = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
    font_sm = ImageFont.truetype(FONT_PATH, 14)
    font_md = ImageFont.truetype(FONT_BOLD, 18)
    font_lg = ImageFont.truetype(FONT_BOLD, 28)
except Exception:
    font_sm = font_md = font_lg = ImageFont.load_default()
