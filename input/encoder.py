# input/encoder.py
from gpiozero import RotaryEncoder, Button

ENC_A = 17
ENC_B = 18
ENC_SW = 27  # кнопка

class Encoder:
    def __init__(self):
        self._on_rotate = None
        self._on_click = None

        # max_steps=0 → бесконечный счёт, wrap=False → не заворачивать
        self._enc = RotaryEncoder(ENC_A, ENC_B, max_steps=0, wrap=False)
        self._btn = Button(ENC_SW, pull_up=True, bounce_time=0.05)

        self._enc.when_rotated_clockwise = self._rot_cw
        self._enc.when_rotated_counter_clockwise = self._rot_ccw
        self._btn.when_pressed = self._pressed

    def on_rotate(self, fn):
        self._on_rotate = fn

    def on_click(self, fn):
        self._on_click = fn

    def _rot_cw(self):
        if self._on_rotate:
            self._on_rotate(+1)

    def _rot_ccw(self):
        if self._on_rotate:
            self._on_rotate(-1)

    def _pressed(self):
        print('.')
        if self._on_click:
            self._on_click()

    def update(self):
        pass
