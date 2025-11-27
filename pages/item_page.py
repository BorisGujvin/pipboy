# pages/item_page.py
import time
from .base import Page
from ui.theme import (
    PADDING, PIP_PANEL, PIP_ACCENT, PIP_TEXT, DIV_LINE, TAB_H,
    font_sm, font_md, font_lg
)

try:
    from affectors.ha_client import toggle as ha_toggle, get_state as ha_get_state
except Exception as e:
    ha_toggle = None
    ha_get_state = None
    print("[ItemPage] affectors.ha_client import failed:", e)


class ItemPage(Page):
    """
    Items = sockets page (kept ItemPage name).

    Auto-active behavior (so main changes not required):
      - as soon as on_encoder/on_click is used -> active=True
      - click on header(BACK) -> returns "back" and active=False

    Requirements:
      - when active: header text "SOCKETS" -> "BACK" (dark/inactive unless selected)
      - header participates in circular selection (sel=-1)
      - selection cycles in circle through header and sockets
      - no underline; selected becomes light green
    """

    def __init__(self, width, height):
        self.W = width
        self.H = height

        self.sockets = [
            {"id": "switch.sonoff_1002036b3f_1", "name": "N1", "state": False},
            {"id": "switch.stub_n2",            "name": "N2", "state": False},
        ]

        self.sel = 0          # -1 header, 0..n-1 sockets
        self.active = False   # auto-set inside on_encoder/on_click

        self.area = (PADDING, TAB_H + PADDING, self.W - PADDING, self.H - PADDING)
        self.row_h = 62
        self.row_gap = 8

        self._last_toggle_ts = 0.0
        self.debounce_sec = 0.35

        self._sync_states()

    # still compatible if you DO call this from main
    def set_active(self, active: bool):
        self.active = active
        if active:
            self.sel = 0

    def _sync_states(self):
        if not ha_get_state:
            return
        for s in self.sockets:
            if s["id"].startswith("switch.sonoff_"):
                try:
                    s["state"] = bool(ha_get_state(s["id"]))
                except Exception as e:
                    print("[SYNC ERROR]", e)

    # ---------- RENDER ----------

    def render(self, draw):
        x0, y0, x1, y1 = self.area
        draw.rectangle(self.area, outline=PIP_ACCENT, fill=PIP_PANEL)

        # Header
        if self.active:
            header_txt = "BACK"
            header_color = PIP_ACCENT if self.sel == -1 else DIV_LINE  # selected bright else dark
        else:
            header_txt = "SOCKETS"
            header_color = PIP_ACCENT

        draw.text((x0 + 10, y0 + 6), header_txt, fill=header_color, font=font_md)
        draw.line([x0 + 8, y0 + 30, x1 - 8, y0 + 30], fill=DIV_LINE, width=2)

        # sockets list
        y = y0 + 38
        for i, s in enumerate(self.sockets):
            self._draw_socket_row(
                draw, x0 + 8, y, x1 - 8, y + self.row_h,
                s, selected=(i == self.sel)
            )
            draw.line([x0 + 8, y + self.row_h + 3, x1 - 8, y + self.row_h + 3],
                      fill=DIV_LINE, width=1)
            y += self.row_h + self.row_gap

        draw.text((x0 + 10, y1 - 18), "tap a socket to toggle",
                  fill=DIV_LINE, font=font_sm)

    def _draw_socket_row(self, draw, x0, y0, x1, y1, s, selected=False):
        mid_y = (y0 + y1) // 2

        name_color = PIP_ACCENT if selected else DIV_LINE
        draw.text((x0 + 6, y0 + 6), s["name"], fill=name_color, font=font_lg)

        sub = "real device" if s["id"].startswith("switch.sonoff_") else "stub"
        draw.text((x0 + 6, y0 + 36), sub, fill=DIV_LINE, font=font_sm)

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

        draw.rounded_rectangle([x0, y0, x1, y1], radius=r,
                               outline=accent, fill=bg, width=2)

        if is_on:
            pad = 2
            right_start = x0 + int(w * 0.38)
            draw.rounded_rectangle(
                [right_start, y0 + pad, x1 - pad, y1 - pad],
                radius=max(0, r-2),
                outline=None,
                fill=accent
            )

        grid_step = 4
        for gx in range(int(x0)+grid_step, int(x1-grid_step), grid_step):
            draw.line([gx, y0+2, gx, y1-2], fill=dim, width=1)

        knob_r = r - 3
        kx = (x0 + w - r) if is_on else (x0 + r)
        ky = y0 + r

        draw.ellipse([kx-knob_r-2, ky-knob_r-2, kx+knob_r+2, ky+knob_r+2],
                     outline=accent, fill=bg, width=2)
        if is_on:
            draw.ellipse([kx-knob_r+1, ky-knob_r+1, kx+knob_r-1, ky+knob_r-1],
                         outline=None, fill=accent)

        on_txt = "ON"
        on_w = draw.textbbox((0, 0), on_txt, font=font_sm)[2]
        on_x = x1 - r - on_w // 2
        ty = y0 + (h - 10) // 2
        draw.text((on_x, ty), on_txt, fill=(bg if is_on else dim), font=font_sm)

    # ---------- INPUT: ENCODER ----------

    def on_encoder(self, delta: int):
        # auto-activate when encoder used inside page
        self.active = True

        n = len(self.sockets)
        total = n + 1  # header + sockets

        idx = 0 if self.sel == -1 else (self.sel + 1)  # 0=header
        idx = (idx + delta) % total
        self.sel = -1 if idx == 0 else (idx - 1)

    def on_click(self):
        # auto-activate when click used inside page
        self.active = True

        if self.sel == -1:
            # leaving page -> back to tabs
            self.active = False
            self.sel = 0
            return "back"

        self._toggle_index(self.sel)

    # ---------- INPUT: TOUCH ----------

    def handle_touch(self, x, y, state):
        idx = self._row_index_at(x, y)
        if idx is None:
            return

        self.sel = idx

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

    # ---------- TOGGLE ----------

    def _toggle_index(self, socket_idx):
        s = self.sockets[socket_idx]
        eid = s["id"]

        if eid.startswith("switch.sonoff_") and ha_toggle:
            try:
                new_state = ha_toggle(eid)
                s["state"] = bool(new_state)
                print(f"[HA TOGGLE] {eid} -> {s['state']}")
                return
            except Exception as e:
                print("[HA TOGGLE ERROR]", e)

        s["state"] = not s["state"]
        print(f"[LOCAL TOGGLE] {eid} -> {s['state']}")
