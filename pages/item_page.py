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

    Final requirements:
      - NO "SOCKETS" text at all; header area reserved for BACK only
      - when active: header shows "BACK" (dark unless selected)
      - when NOT active: header empty, sockets + toggles are dim/gray (inactive look)
      - encoder cycles in circle through header and sockets, click on header -> "back"
      - selected item is highlighted only by color (no underline)
    """

    def __init__(self, width, height):
        self.W = width
        self.H = height

        self.sockets = [
            {"id": "switch.sonoff_1002036b3f_1", "name": "N1", "state": False},
            {"id": "switch.stub_n2",            "name": "N2", "state": False},
        ]

        # sel = -1 => header ("BACK" when active)
        # sel = 0..n-1 => sockets
        self.sel = 0
        self.active = False

        self.area = (PADDING, TAB_H + PADDING, self.W - PADDING, self.H - PADDING)
        self.row_h = 62
        self.row_gap = 8

        self._last_toggle_ts = 0.0
        self.debounce_sec = 0.35

        self._sync_states()

    def set_active(self, active: bool):
        self.active = active
        if a
