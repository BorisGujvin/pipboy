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

    # focus: "tabs" (меню вкладок) или "page" (внутри вкладки)
    focus = "tabs"

    # ROTATE handler: роутим по focus
    def handle_rotate(d):
        nonlocal focus
        if focus == "tabs":
            tabbar.rotate(d)
        else:
            page = pages[tabbar.active]
            if hasattr(page, "on_encoder"):
                page.on_encoder(d)

    enc.on_rotate(handle_rotate)

    try:
        while True:
            img = Image.new('RGB', (W, H), PIP_BG)
            draw = ImageDraw.Draw(img)

            # UI
            tabbar.render(draw)
            pages[tabbar.active].render(draw)

            # Push frame
            frame = Display.pil_to_rgb565(img)
            disp.push_frame_rgb565(frame)

            # Touch/Encoder burst
            t0 = time.time()
            while time.time() - t0 < 0.03:
                enc.update()

                # --- ENCODER CLICK ---
                # Пытаемся максимально безопасно достать событие клика:
                clicked = False
                if hasattr(enc, "was_clicked"):
                    clicked = enc.was_clicked()
                elif hasattr(enc, "clicked"):
                    # если Encoder делает флаг
                    clicked = bool(enc.clicked)
                    if clicked:
                        enc.clicked = False
                elif hasattr(enc, "button_pressed"):
                    clicked = enc.button_pressed()

                if clicked:
                    if focus == "tabs":
                        # вход во вкладку
                        focus = "page"
                    else:
                        # клик внутри страницы
                        page = pages[tabbar.active]
                        res = page.on_click() if hasattr(page, "on_click") else None
                        if res == "back":
                            focus = "tabs"

                # --- TOUCH ---
                pos = touch.read(samples=5)
                if pos is not None:
                    x, y = pos
                    idx = tabbar.hit_test(x, y)
                    if idx is not None:
                        tabbar.active = idx
                        focus = "tabs"   # тап по табам всегда возвращает в меню
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
