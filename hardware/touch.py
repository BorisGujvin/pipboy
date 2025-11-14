# hardware/touch.py
import os
import json
import spidev
import numpy as np

from config import (
    SPI_TOUCH_BUS,
    SPI_TOUCH_DEV,
    SPI_TOUCH_HZ,
    TOUCH_CAL_FILE,
    TOUCH_SWAP_XY_DEFAULT,
)
from hardware.display import W, H  # чтобы тач знал размеры экрана

CMD_X, CMD_Y, CMD_Z1, CMD_Z2 = 0xD0, 0x90, 0xB0, 0xC0

class Touch:
    def __init__(self):
        self.tp = spidev.SpiDev()
        self.tp.open(SPI_TOUCH_BUS, SPI_TOUCH_DEV)
        self.tp.max_speed_hz = SPI_TOUCH_HZ
        self.tp.mode = 0

        # mat + флаги
        if os.path.exists(TOUCH_CAL_FILE):
            with open(TOUCH_CAL_FILE, "r") as f:
                cfg = json.load(f)
            self.calM = np.array(cfg["M"], dtype=float)
            self.CAL_FLIP_X = bool(cfg.get("CAL_FLIP_X", False))
            self.CAL_FLIP_Y = bool(cfg.get("CAL_FLIP_Y", False))
            self.TOUCH_SWAP_XY = bool(cfg.get("TOUCH_SWAP_XY", TOUCH_SWAP_XY_DEFAULT))
        else:
            self.calM = np.array(
                [[W/2048.0, 0, -W*0.1],
                 [0, H/2048.0, -H*0.1]],
                dtype=float,
            )
            self.CAL_FLIP_X = self.CAL_FLIP_Y = False
            self.TOUCH_SWAP_XY = TOUCH_SWAP_XY_DEFAULT

    def _tp_read12(self, cmd):
        resp = self.tp.xfer2([cmd, 0x00, 0x00])
        return ((resp[1] << 8) | resp[2]) >> 3

    def _tp_sample(self, samples=7):
        z1, z2 = self._tp_read12(CMD_Z1), self._tp_read12(CMD_Z2)
        if z1 == 0 or z2 == 0:
            return None
        xs, ys = [], []
        for _ in range(samples):
            y = self._tp_read12(CMD_Y)
            x = self._tp_read12(CMD_X)
            xs.append(x); ys.append(y)
        xs.sort(); ys.sort()
        xr, yr = xs[len(xs)//2], ys[len(ys)//2]
        if xr < 10 or yr < 10 or xr > 4090 or yr > 4090:
            return None
        return xr, yr

    def _apply_affine(self, xr, yr):
        if self.TOUCH_SWAP_XY:
            xr, yr = yr, xr
        v = np.array([xr, yr, 1.0], dtype=float)
        out = self.calM @ v
        x, y = float(out[0]), float(out[1])

        if self.CAL_FLIP_X:
            x = (W - 1) - x
        if self.CAL_FLIP_Y:
            y = (H - 1) - y

        x = int(0 if x < 0 else (W-1 if x > W-1 else round(x)))
        y = int(0 if y < 0 else (H-1 if y > H-1 else round(y)))
        return x, y

    def read(self, samples=5):
        s = self._tp_sample(samples=samples)
        if s is None:
            return None
        xr, yr = s
        return self._apply_affine(xr, yr)

    def close(self):
        self.tp.close()
