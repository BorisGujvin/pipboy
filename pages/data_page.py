# pages/data_page.py
import time
from .base import Page
from ui.theme import PADDING, PIP_TEXT, PIP_TEXT_DIM, TAB_H, font_lg, font_sm

class DataPage(Page):
    def __init__(self, width, height):
        self.W = width
        self.H = height

    def render(self, draw):
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        draw.text((PADDING, TAB_H + PADDING), "DATA", fill=PIP_TEXT, font=font_lg)
        draw.text((PADDING, TAB_H + PADDING + 40), f"Time: {now}",
                  fill=PIP_TEXT, font=font_sm)
        draw.text((PADDING, self.H - 24),
                  "(demo) Add map, quests, radio here",
                  fill=PIP_TEXT_DIM, font=font_sm)

    def handle_touch(self, x, y, state):
        return

    def on_encoder(self, delta: int):
        pass

    def on_click(self):
        pass