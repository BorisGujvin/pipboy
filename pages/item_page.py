# pages/item_page.py
from .base import Page
from ui.theme import PADDING, PIP_PANEL, PIP_ACCENT, PIP_TEXT, DIV_LINE, TAB_H, font_sm

class ItemPage(Page):
    def __init__(self, width, height):
        self.W = width
        self.H = height
        self.items = [f"Stimpak x{i}" for i in range(1, 12)] + \
                     ["10mm Rounds x24", "Cram", "Vault Suit"]
        self.scroll = 0
        self.state = {"dragging": False, "last": None}
        self.area = (PADDING, TAB_H + PADDING, self.W - PADDING, self.H - PADDING)

    def render(self, draw):
        x0,y0,x1,y1 = self.area
        draw.rectangle(self.area, outline=PIP_ACCENT, fill=PIP_PANEL)

        x, y = x0 + 8, y0 + 8
        line_h = 24
        start = self.scroll
        end = min(len(self.items), start + (y1-y0-16)//line_h)
        for i in range(start, end):
            draw.text((x, y), f"• {self.items[i]}", fill=PIP_TEXT, font=font_sm)
            y += line_h

        # scrollbar
        total = max(1, len(self.items))
        vis = max(1, end - start)
        track_x = x1 - 10
        track_y0, track_y1 = y0+6, y1-6
        draw.line([track_x, track_y0, track_x, track_y1], fill=DIV_LINE, width=2)
        thumb_len = max(12, int((vis/total) * (track_y1 - track_y0)))
        ratio = start/(total-vis) if total > vis else 0.0
        thumb_y0 = int(track_y0 + ratio * (track_y1 - track_y0 - thumb_len))
        draw.rectangle([track_x-3, thumb_y0, track_x+3, thumb_y0+thumb_len],
                       fill=PIP_ACCENT)

    def handle_touch(self, x, y, state):
        x0,y0,x1,y1 = self.area
        if x0 <= x <= x1 and y0 <= y <= y1:
            if not self.state.get('dragging'):
                self.state['dragging'] = True
                self.state['last'] = y
            else:
                dy = y - self.state.get('last', y)
                if abs(dy) >= 6:
                    delta = -1 if dy > 0 else 1
                    self.scroll = max(0, min(len(self.items)-1, self.scroll + delta))
                    self.state['last'] = y
        else:
            self.state.update(dragging=False, last=None)
