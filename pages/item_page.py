import time
from .base import Page
from ui.theme import (
    PADDING, PIP_PANEL, PIP_ACCENT, PIP_TEXT, DIV_LINE, TAB_H,
    font_sm, font_md, font_lg)
from affectors.ha_client import toggle as ha_toggle, get_state as ha_get_state

class ItemPage(Page):
    def __init__(self, width, height):
        self.W = width
        self.H = height

        self.sockets = [
            {"id": "switch.sonoff_1002036b3f_1", "name": "First", "state": False},
            {"id": "switch.stub_n2",            "name": "Fake", "state": False},
        ]

        self.selected = 0
        self.area = (PADDING, TAB_H + PADDING, self.W - PADDING, self.H - PADDING)

        # layout
        self.row_h = 62
        self.row_gap = 8

        # debounce
        self._last_toggle_ts = 0.0
        self.debounce_sec = 0.35

        self._sync_states()

    def _sync_states(self):
        if not ha_get_state:
            return
        for s in self.sockets:
            if s["id"].startswith("switch.sonoff_"):
                try:
                    s["state"] = bool(ha_get_state(s["id"]))
                except Exception as e:
                    print("[SYNC ERROR]", e)

    def render(self, draw):
        x0, y0, x1, y1 = self.area
        draw.rectangle(self.area, outline=PIP_ACCENT, fill=PIP_PANEL)
        back_color = PIP_ACCENT if self.selected == -1 else DIV_LINE
        back_text = "<< BACK"
        draw.text((x0 + 8, y0 + 6), back_text, fill=back_color, font=font_sm)

        # header
        draw.text((x0 + 10, y0 + 6), "SOCKETS", fill=PIP_ACCENT, font=font_md)
        draw.line([x0 + 8, y0 + 30, x1 - 8, y0 + 30], fill=DIV_LINE, width=2)

        # list
        y = y0 + 38
        for i, s in enumerate(self.sockets):
            self._draw_row(
                draw,
                x0 + 8, y,
                x1 - 8, y + self.row_h,
                s,
                selected=(i == self.selected)
            )

            # subtle divider between rows (no frame)
            draw.line([x0 + 8, y + self.row_h + 3, x1 - 8, y + self.row_h + 3],
                      fill=DIV_LINE, width=1)

            y += self.row_h + self.row_gap

        # footer hint
        draw.text((x0 + 10, y1 - 18), "tap a socket to toggle", fill=DIV_LINE, font=font_sm)

    def _draw_row(self, draw, x0, y0, x1, y1, s, selected=False):
        mid_y = (y0 + y1) // 2

        # name only (highlight when selected)
        name_x = x0 + 6
        name_color = PIP_ACCENT if selected else DIV_LINE
        draw.text((name_x, y0 + 6), s["name"], fill=name_color, font=font_lg)

        # optional subtext (dim)
        sub = "real device" if s["id"].startswith("switch.sonoff_") else "stub"
        draw.text((name_x, y0 + 36), sub, fill=DIV_LINE, font=font_sm)

        # Fallout toggle on right
        toggle_w = 120
        toggle_h = 38
        tx1 = x1 - 6
        tx0 = tx1 - toggle_w
        ty0 = mid_y - toggle_h // 2
        ty1 = ty0 + toggle_h
        self._draw_toggle(draw, tx0, ty0, tx1, ty1, s["state"])

    def _draw_toggle(self, draw, x0, y0, x1, y1, is_on):
        w = x1 - x0
        h = y1 - y0
        r = h // 2

        bg = PIP_PANEL
        accent = PIP_ACCENT
        dim = DIV_LINE

        # Track outline
        draw.rounded_rectangle([x0, y0, x1, y1], radius=r, outline=accent, fill=bg, width=2)

        # ON fill (RIGHT segment only)
        if is_on:
            pad = 2
            right_start = x0 + int(w * 0.38)
            draw.rounded_rectangle(
                [right_start, y0 + pad, x1 - pad, y1 - pad],
                radius=max(0, r-2),
                outline=None,
                fill=accent
            )

        # subtle vertical scan/grid inside track
        grid_step = 4
        for gx in range(int(x0)+grid_step, int(x1-grid_step), grid_step):
            draw.line([gx, y0+2, gx, y1-2], fill=dim, width=1)

        # Knob position
        knob_r = r - 3
        kx = (x0 + w - r) if is_on else (x0 + r)
        ky = y0 + r

        # Knob outer ring
        draw.ellipse([kx-knob_r-2, ky-knob_r-2, kx+knob_r+2, ky+knob_r+2],
                     outline=accent, fill=bg, width=2)
        # Knob inner fill when ON
        if is_on:
            draw.ellipse([kx-knob_r+1, ky-knob_r+1, kx+knob_r-1, ky+knob_r-1],
                         outline=None, fill=accent)

        # Only "ON" label on the right (no OFF label)
        on_txt = "ON"
        on_w = draw.textbbox((0, 0), on_txt, font=font_sm)[2]
        on_x = x1 - r - on_w // 2
        ty = y0 + (h - 10) // 2

        draw.text((on_x, ty), on_txt, fill=(bg if is_on else dim), font=font_sm)

    def handle_touch(self, x, y, state):
        idx = self._row_index_at(x, y)
        if idx is None:
            return

        self.selected = idx

        now = time.time()
        if now - self._last_toggle_ts < self.debounce_sec:
            return
        self._last_toggle_ts = now

        self._toggle_index(idx)

    def _row_index_at(self, x, y):
        x0, y0, x1, y1 = self.area
        if not (x0 <= x <= x1 and y0 <= y <= y1):
            return None

        list_y0 = y0 + 38
        if y < list_y0:
            return None

        idx = int((y - list_y0) // (self.row_h + self.row_gap))
        if 0 <= idx < len(self.sockets):
            return idx
        return None

    def _toggle_index(self, idx):
        s = self.sockets[idx]
        eid = s["id"]

        if eid.startswith("switch.sonoff_") and ha_toggle:
            try:
                new_state = ha_toggle(eid)
                s["state"] = bool(new_state)
                return
            except Exception as e:
                print("[HA TOGGLE ERROR]", e)

        s["state"] = not s["state"]

    def on_encoder(self, delta: int):
        """
        Энкодер внутри Items:
        delta +1/-1 двигает выделение.
        selected == -1 это BACK.
        """
        n = len(self.sockets)

        if self.selected == -1 and delta > 0:
            self.selected = 0
            return

        if self.selected == 0 and delta < 0:
            self.selected = -1
            return

        if self.selected >= 0:
            self.selected = max(0, min(n - 1, self.selected + delta))


    def on_click(self):
        """
        Клик энкодера внутри Items:
        - если BACK выбран -> выйти в табы
        - иначе toggle выбранную розетку
        """
        if self.selected == -1:
            return "back"

        self._toggle_index(self.selected)
