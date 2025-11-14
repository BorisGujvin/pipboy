# hardware/display.py
import time
import spidev
import numpy as np
import RPi.GPIO as GPIO
from PIL import Image
from config import (
    LCD_DC_PIN, LCD_RST_PIN,
    SPI_LCD_BUS, SPI_LCD_DEV, SPI_LCD_HZ,
    NATIVE_WIDTH, NATIVE_HEIGHT,
    LCD_ROTATION, LCD_FLIP_X, LCD_FLIP_Y,
    MAD_MY, MAD_MX, MAD_MV, MAD_BGR,
)

# рассчитываем MADCTL и размеры экрана один раз на основе конфига
baseW, baseH = NATIVE_WIDTH, NATIVE_HEIGHT

mad_map = {
    0: MAD_BGR,
    90: MAD_MV | MAD_MX | MAD_BGR,
    180: MAD_MY | MAD_MX | MAD_BGR,
    270: MAD_MY | MAD_MV | MAD_BGR,
}
mad = mad_map[LCD_ROTATION]
if LCD_FLIP_X:
    mad ^= MAD_MX
if LCD_FLIP_Y:
    mad ^= MAD_MY

if mad & MAD_MV:
    W, H = baseH, baseW
else:
    W, H = baseW, baseH

class Display:
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(LCD_DC_PIN, GPIO.OUT)
        GPIO.setup(LCD_RST_PIN, GPIO.OUT)

        self.lcd = spidev.SpiDev()
        self.lcd.open(SPI_LCD_BUS, SPI_LCD_DEV)
        self.lcd.max_speed_hz = SPI_LCD_HZ
        self.lcd.mode = 0

        self._init_lcd()

    def _dc_cmd(self):
        GPIO.output(LCD_DC_PIN, 0)

    def _dc_data(self):
        GPIO.output(LCD_DC_PIN, 1)

    def _hw_reset(self):
        GPIO.output(LCD_RST_PIN, 1); time.sleep(0.01)
        GPIO.output(LCD_RST_PIN, 0); time.sleep(0.02)
        GPIO.output(LCD_RST_PIN, 1); time.sleep(0.12)

    def _wcmd(self, c: int):
        self._dc_cmd()
        self.lcd.writebytes([c & 0xFF])

    def _wdat_bytes(self, b: bytes):
        self._dc_data()
        mv = memoryview(b)
        CH = 4096
        for i in range(0, len(mv), CH):
            self.lcd.writebytes2(mv[i:i+CH])

    def _w16(self, v: int):
        self._wdat_bytes(bytes([(v >> 8) & 0xFF, v & 0xFF]))

    def set_window(self, x0, y0, x1, y1):
        x0 = max(0, min(W-1, x0)); x1 = max(0, min(W-1, x1))
        y0 = max(0, min(H-1, y0)); y1 = max(0, min(H-1, y1))
        if x1 < x0: x0, x1 = x1, x0
        if y1 < y0: y0, y1 = y1, y0
        self._wcmd(0x2A); self._w16(x0); self._w16(x1)
        self._wcmd(0x2B); self._w16(y0); self._w16(y1)
        self._wcmd(0x2C)

    def _init_lcd(self):
        self._hw_reset()
        self._wcmd(0x01); time.sleep(0.12)
        self._wcmd(0x11); time.sleep(0.12)
        self._wcmd(0x3A); self._wdat_bytes(b"\x55")
        self._wcmd(0x36); self._wdat_bytes(bytes([mad]))
        self._wcmd(0x29); time.sleep(0.02)
        self._wcmd(0x13); time.sleep(0.02)

    def push_frame_rgb565(self, rgb565):
        self.set_window(0, 0, W-1, H-1)
        if isinstance(rgb565, np.ndarray):
            if rgb565.ndim == 3:
                data = rgb565.reshape(-1)
            else:
                data = rgb565
            self._wdat_bytes(data.tobytes())
        else:
            self._wdat_bytes(rgb565)

    @staticmethod
    def pil_to_rgb565(img: Image.Image) -> np.ndarray:
        if img.mode != "RGB":
            img = img.convert("RGB")
        arr = np.asarray(img, dtype=np.uint8)
        r = (arr[..., 0].astype(np.uint16) >> 3) << 11
        g = (arr[..., 1].astype(np.uint16) >> 2) << 5
        b = (arr[..., 2].astype(np.uint16) >> 3)
        rgb565 = (r | g | b).astype(np.uint16)
        hi = (rgb565 >> 8).astype(np.uint8)
        lo = (rgb565 & 0xFF).astype(np.uint8)
        out = np.dstack((hi, lo))
        return out

    def cleanup(self):
        self.lcd.close()
        GPIO.cleanup()
