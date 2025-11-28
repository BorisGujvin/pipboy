# main.py
import time
from PIL import Image, ImageDraw

from hardware.display import Display, W, H
from hardware.touch import Touch
from ui.theme import PIP_BG
from ui.tabbar import TabBar
from pages.stat_page import StatPage
from pages.item_page import ItemPage
from pages.data_page import DataPage
from pages.body_page import BodyPage
from config import TAB_NAMES
from input.encoder import Encoder


def main():
    disp = Display()
    touch = Touch()
    tabbar = TabBar(W, TAB_NAMES)
    enc = Encoder()

    pages = [
        BodyPage(W, H),
        StatPage(W, H),
        ItemPage(W, H),
        DataPage(W, H),
    ]

    focus = "tabs"

    def set_page_active(active: bool):
        page = pages[tabbar.active]
        if hasattr(page, "set_active"):
            page.set_active(active)

    def handle_rotate(d):
        nonlocal focus
        if focus == "tabs":
            tabbar.rotate(d)
        else:
            page = pages[tabbar.active]
            if hasattr(page, "on_encoder"):
                page.on_encoder(d)

    def handle_click():
        nonlocal focus
        if focus == "tabs":
            # ВХОД во вкладку -> сразу активируем страницу
            focus = "page"
            set_page_active(True)
        else:
            # клик внутри страницы
            page = pages[tabbar.active]
            res = page.on_click() if hasattr(page, "on_click") else None
            if res == "back":
                # ВЫХОД из вкладки -> деактивируем
                set_page_active(False)
                focus = "tabs"

    enc.on_rotate(handle_rotate)
    enc.on_click(handle_click)

    try:
        while True:
            img = Image.new('RGB', (W, H), PIP_BG)
            draw = ImageDraw.Draw(img)

            tabbar.render(draw)
            pages[tabbar.active].render(draw)

            frame = Display.pil_to_rgb565(img)
            disp.push_frame_rgb565(frame)

            t0 = time.time()
            while time.time() - t0 < 0.03:
                enc.update()

                pos = touch.read(samples=5)
                if pos is not None:
                    x, y = pos
                    idx = tabbar.hit_test(x, y)
                    if idx is not None:
                        set_page_active(False)
                        tabbar.active = idx
                        focus = "page"
                        set_page_active(True)
                    else:
                        pages[tabbar.active].handle_touch(x, y, {})
                time.sleep(0.002)

    except KeyboardInterrupt:
        pass
    finally:
        touch.close()
        disp.cleanup()


if __name__ == "__main__":
    main()
