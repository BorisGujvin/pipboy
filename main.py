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

    enc.on_rotate(lambda d: tabbar.rotate(d))

    pages = [
        BodyPage(W, H),
        StatPage(W, H),
        ItemPage(W, H),
        DataPage(W, H),
    ]

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

            # Touch burst
            t0 = time.time()
            while time.time() - t0 < 0.03:
                enc.update()
                pos = touch.read(samples=5)
                if pos is not None:
                    x, y = pos
                    idx = tabbar.hit_test(x, y)
                    if idx is not None:
                        tabbar.active = idx
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
