# ui/tabbar.py
from .theme import TAB_BG, TAB_ACTIVE, DIV_LINE, TAB_H, PADDING, PIP_TEXT, font_md
from .textutils import measure_text

class TabBar:
    def __init__(self, width, tabs):
        self.width = width
        self.tabs = tabs
        self.active = 0
        self.tab_width = width // len(tabs)
        self.zones = [
            (i*self.tab_width, 0, (i+1)*self.tab_width-1, TAB_H)
            for i in range(len(tabs))
        ]

    def render(self, draw):
        # background bar
        draw.rectangle([0, 0, self.width-1, TAB_H], fill=TAB_BG)
        for i, name in enumerate(self.tabs):
            x0, y0, x1, y1 = self.zones[i]
            fill = TAB_ACTIVE if i == self.active else TAB_BG
            draw.rectangle([x0, 0, x1, TAB_H], fill=fill)
            tw, th = measure_text(draw, name, font_md)
            draw.text((x0 + (self.tab_width - tw)//2,
                       (TAB_H - th)//2),
                      name, fill=PIP_TEXT, font=font_md)
        draw.line([0, TAB_H, self.width-1, TAB_H], fill=DIV_LINE)

    def hit_test(self, x, y):
        for i, (x0, y0, x1, y1) in enumerate(self.zones):
            if x0 <= x <= x1 and y0 <= y <= y1:
                return i
        return None

    def rotate(self, direction):
        if direction > 0:
            self.active = (self.active + 1) % len(self.tabs)
        else:
            self.active = (self.active - 1) % len(self.tabs)
