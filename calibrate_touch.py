#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import time
import json
import numpy as np
import spidev

from PIL import Image, ImageDraw

from config import (
    SPI_TOUCH_BUS,
    SPI_TOUCH_DEV,
    SPI_TOUCH_HZ,
    TOUCH_CAL_FILE,
)

from hardware.display import Display, W, H


# ===== RAW TOUCH (XPT2046) =====

CMD_X, CMD_Y, CMD_Z1, CMD_Z2 = 0xD0, 0x90, 0xB0, 0xC0

class RawTouch:
    def __init__(self):
        self.tp = spidev.SpiDev()
        self.tp.open(SPI_TOUCH_BUS, SPI_TOUCH_DEV)
        self.tp.max_speed_hz = SPI_TOUCH_HZ
        self.tp.mode = 0

    def _read12(self, cmd):
        resp = self.tp.xfer2([cmd, 0x00, 0x00])
        return ((resp[1] << 8) | resp[2]) >> 3

    def sample(self, samples=7):
        """
        Возвращает сырые (xr, yr) от АЦП тача или None, если нет касания.
        """
        z1, z2 = self._read12(CMD_Z1), self._read12(CMD_Z2)
        if z1 == 0 or z2 == 0:
            return None

        xs, ys = [], []
        for _ in range(samples):
            y = self._read12(CMD_Y)
            x = self._read12(CMD_X)
            xs.append(x)
            ys.append(y)

        xs.sort()
        ys.sort()
        xr, yr = xs[len(xs)//2], ys[len(ys)//2]

        if xr < 10 or yr < 10 or xr > 4090 or yr > 4090:
            return None

        return xr, yr

    def close(self):
        self.tp.close()


# ===== КАЛИБРОВКА =====

def draw_target(draw: ImageDraw.ImageDraw, x, y, idx, total):
    r = 12
    # крест
    draw.line((x - r, y, x + r, y), fill=(0, 255, 0), width=2)
    draw.line((x, y - r, x, y + r), fill=(0, 255, 0), width=2)
    msg = f"Tap target {idx+1}/{total}"
    tw, th = draw.textlength(msg), 14
    draw.text((10, H - 20), msg, fill=(0, 255, 0))


def collect_points(disp: Display, rt: RawTouch):
    margin = 30
    screen_pts = [
        (margin, margin),              # левый верх
        (W - margin, margin),          # правый верх
        (W - margin, H - margin),      # правый низ
        (margin, H - margin),          # левый низ
        (W // 2, H // 2),              # центр
    ]

    raw_pts = []

    total = len(screen_pts)

    for i, (sx, sy) in enumerate(screen_pts):
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        draw_target(draw, sx, sy, i, total)
        frame = Display.pil_to_rgb565(img)
        disp.push_frame_rgb565(frame)

        print(f"Ткни по цели #{i+1}/{total} (экран: {sx},{sy})")

        # ждём нажатие
        while True:
            s = rt.sample(samples=7)
            if s is not None:
                xr, yr = s
                print(f"  raw = ({xr}, {yr})")
                raw_pts.append((xr, yr))
                time.sleep(0.5)  # дать время отпустить палец
                break
            time.sleep(0.02)

    return screen_pts, raw_pts


def compute_affine(screen_pts, raw_pts):
    """
    Ищем матрицу M (2x3), такую что:
      [x_screen]   [a b c] [xr]
      [y_screen] = [d e f] [yr]
                           [1 ]
    """
    A = []
    bx = []
    by = []

    for (xr, yr), (xs, ys) in zip(raw_pts, screen_pts):
        A.append([xr, yr, 1.0])
        bx.append(xs)
        by.append(ys)

    A = np.array(A, dtype=float)
    bx = np.array(bx, dtype=float)
    by = np.array(by, dtype=float)

    params_x, *_ = np.linalg.lstsq(A, bx, rcond=None)
    params_y, *_ = np.linalg.lstsq(A, by, rcond=None)

    M = np.vstack([params_x, params_y])  # shape (2,3)
    return M


def main():
    print(f"Калибровка для экрана {W}x{H}")
    disp = Display()
    rt = RawTouch()

    try:
        screen_pts, raw_pts = collect_points(disp, rt)

        print("Экранные точки:", screen_pts)
        print("Сырые точки:", raw_pts)

        M = compute_affine(screen_pts, raw_pts)
        print("Матрица M:")
        print(M)

        calib = {
            "M": M.tolist(),
            "CAL_FLIP_X": False,
            "CAL_FLIP_Y": False,
            # После калибровки Touch будет брать это из файла,
            # а не из TOUCH_SWAP_XY_DEFAULT.
            "TOUCH_SWAP_XY": False,
        }

        with open(TOUCH_CAL_FILE, "w") as f:
            json.dump(calib, f, indent=2)

        print(f"Калибровка сохранена в {TOUCH_CAL_FILE}")

        # финальный экран
        img = Image.new("RGB", (W, H), (0, 0, 0))
        draw = ImageDraw.Draw(img)
        msg = "Calibration OK"
        draw.text((20, H//2 - 10), msg, fill=(0, 255, 0))
        frame = Display.pil_to_rgb565(img)
        disp.push_frame_rgb565(frame)

    finally:
        rt.close()
        disp.cleanup()


if __name__ == "__main__":
    main()
