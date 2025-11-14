# config.py
"""
Global configuration for the Pip-Boy project.
Central place for constants used across modules.
"""

# ----- Display Config -----

# Physical SPI pins for ST7796S
LCD_DC_PIN = 24
LCD_RST_PIN = 25

SPI_LCD_BUS = 0
SPI_LCD_DEV = 0
SPI_LCD_HZ = 16_000_000

# Native screen size of ST7796S
NATIVE_WIDTH = 320
NATIVE_HEIGHT = 480

# Screen rotation (0, 90, 180, 270)
LCD_ROTATION = 90

# Extra flips
LCD_FLIP_X = False
LCD_FLIP_Y = True

# MADCTL controller bits
MAD_MY = 0x80
MAD_MX = 0x40
MAD_MV = 0x20
MAD_BGR = 0x08


# ----- Touch Config -----

SPI_TOUCH_BUS = 0
SPI_TOUCH_DEV = 1
SPI_TOUCH_HZ = 2_000_000

TOUCH_CAL_FILE = "touch_cal.json"
TOUCH_SWAP_XY_DEFAULT = True


# ----- UI Config -----

TAB_NAMES = ["BODY", "STAT", "ITEM", "DATA"]

TAB_HEIGHT = 44
PADDING = 10

# Fonts (can be overridden)
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"

FONT_SIZE_SM = 14
FONT_SIZE_MD = 18
FONT_SIZE_LG = 28

# Frame rate (main loop)
FRAME_TIME = 0.03      # 30 ms per frame (~33 FPS)
TOUCH_POLL_TIME = 0.002


# ----- Color Theme -----

COLOR_BG = (16, 24, 16)
COLOR_PANEL = (24, 40, 24)
COLOR_ACCENT = (80, 200, 120)
COLOR_TEXT = (180, 255, 200)
COLOR_TEXT_DIM = (120, 180, 140)

COLOR_TAB_BG = (10, 20, 10)
COLOR_TAB_ACTIVE = (40, 90, 60)
COLOR_DIVIDER = (50, 90, 60)
