# pages/stat_page.py
from .base import Page
from ui.theme import PADDING, PIP_TEXT, PIP_TEXT_DIM, PIP_ACCENT, font_lg, font_sm
from ui.theme import TAB_H
from ui.textutils import measure_text

class StatPage(Page):
    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.hp = 87
        self.ap = 56
        self.rad = 12

    def _bar(self, draw, x, y, val, col):
        wbar, hbar = 240, 16
        draw.rectangle([x, y, x+wbar, y+hbar], outline=PIP_ACCENT, fill=(24,40,24))
        wval = max(0, min(wbar, int(wbar*val/100)))
        draw.rectangle([x, y, x+wval, y+hbar], fill=col)

    def render(self, draw):
        y = TAB_H + PADDING
        draw.text((PADDING, y), f"HP: {self.hp}", fill=PIP_TEXT, font=font_lg); y += 40
        draw.text((PADDING, y), f"AP: {self.ap}", fill=PIP_TEXT, font=font_lg); y += 40
        draw.text((PADDING, y), f"RAD: {self.rad}", fill=PIP_TEXT, font=font_lg)

        self._bar(draw, 220, TAB_H + 20, self.hp, (60, 220, 120))
        self._bar(draw, 220, TAB_H + 50, self.ap, (60, 160, 220))
        self._bar(draw, 220, TAB_H + 80, min(100, self.rad), (220, 140, 60))

        draw.text((PADDING, self.H - 24),
                  "Tap tabs to switch · Tap and hold = draw",
                  fill=PIP_TEXT_DIM, font=font_sm)

    def handle_touch(self, x, y, state):
        # тут пока ничего, можно потом добавить интерактив
        return

    def on_encoder(self, delta: int):
            pass

    def on_click(self):
        pass
