# pages/body_page.py
from .base import Page
from ui.theme import (
    PADDING,
    TAB_H,
    PIP_PANEL,
    PIP_ACCENT,
)
from PIL import Image


class BodyPage(Page):
    """
    Таб BODY: картинка вписывается по ширине,
    сверху и снизу лишнее отрезается.
    """

    def __init__(self, width, height):
        self.W = width
        self.H = height

        # область под картинку (рабочая область страницы)
        area_w = self.W - 2 * PADDING
        area_h = self.H - TAB_H - 2 * PADDING

        # ЗДЕСЬ имя файла — поменяй при необходимости
        img = Image.open("assets/body.jpg").convert("RGB")

        src_w, src_h = img.size

        # 1) Масштабируем по ширине (вписываем ровно в area_w)
        scale = area_w / src_w
        scaled_h = int(src_h * scale)
        img_scaled = img.resize((area_w, scaled_h), Image.LANCZOS)

        # 2) Если высота вылезает за область — режем по центру
        if scaled_h > area_h:
            top = (scaled_h - area_h) // 2
            bottom = top + area_h
            self.img_body = img_scaled.crop((0, top, area_w, bottom))
        else:
            # если вдруг картинка ниже, чем area_h — не режем
            self.img_body = img_scaled

        # панель по размеру итоговой картинки
        self.panel_left = PADDING
        self.panel_top = TAB_H + PADDING
        self.panel_right = self.panel_left + self.img_body.size[0]
        self.panel_bottom = self.panel_top + self.img_body.size[1]

    def _get_base_image(self, draw):
        """
        Достаём базовый буфер из ImageDraw.
        На Pillow>=10 это draw._image (PIL.Image),
        на старых — draw.im (ImagingCore).
        """
        img = getattr(draw, "_image", None)
        if img is None:
            img = getattr(draw, "im", None)
        return img

    def render(self, draw):
        base_img = self._get_base_image(draw)
        if base_img is None:
            # на всякий пожарный — просто прямоугольник
            draw.rectangle(
                (self.panel_left, self.panel_top,
                 self.panel_right, self.panel_bottom),
                outline=PIP_ACCENT,
                fill=PIP_PANEL,
            )
            return

        # рисуем панель
        draw.rectangle(
            (self.panel_left, self.panel_top,
             self.panel_right, self.panel_bottom),
            outline=PIP_ACCENT,
            fill=PIP_PANEL,
        )

        # вставляем картинку по панели
        w, h = self.img_body.size
        x, y = self.panel_left, self.panel_top
        box = (x, y, x + w, y + h)

        # ImagingCore / Image — берём что есть
        src = getattr(self.img_body, "im", self.img_body)
        base_img.paste(src, box)

    def handle_touch(self, x, y, state):
        return

    def on_encoder(self, delta: int):
            pass

    def on_click(self):
            pass
