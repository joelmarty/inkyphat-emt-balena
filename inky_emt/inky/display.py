from PIL import Image, ImageFont, ImageDraw
from PIL.ImageFont import FreeTypeFont
from font_connection_iii import ConnectionIII
from unidecode import unidecode

from inky_emt.model import ArrivalInfo, Arrival
from typing import List

INCIDENT_MARK = '*'
MAX_TITLE_SIZE = 20


class ArrivalDisplay:

    def __init__(self, display_type: str, color: str, mock=False):
        self._init_display(color, mock, display_type)
        self._init_canvas()
        self._draw_background()

    def _init_display(self, color, mock, type):
        if mock:
            from inky import InkyMockPHAT as InkyPHAT
            from inky import InkyMockWHAT as InkyWHAT
        else:
            from inky import InkyPHAT
            from inky import InkyWHAT
        if type == 'phat':
            self._display = InkyPHAT(color)
            self._scale_size = 1.0
            self._padding = 2
        elif type == 'what':
            self._display = InkyWHAT(color)
            self._scale_size = 2.20
            self._padding = 15

    def _init_canvas(self):
        """must be called after _init_display"""
        img = Image.new("P", (self._display.WIDTH, self._display.HEIGHT))
        self._img = img
        self._draw = ImageDraw.Draw(img)

    def _draw_background(self):
        self._display.set_border(self._display.YELLOW)
        for y in range(0, self._display.height):
            for x in range(0, self._display.width):
                self._img.putpixel((x, y), self._display.BLACK)

    def _adjust_font_size(self, text) -> FreeTypeFont:
        font_size = MAX_TITLE_SIZE
        while True:
            font = ImageFont.truetype(ConnectionIII,
                                      int(font_size * self._scale_size))
            title_w, title_h = font.getsize(text)
            if title_w + self._padding > self._display.WIDTH:
                font_size -= 1
            else:
                return font

    def _draw_title(self, title: str, incident: bool):
        title_font = self._adjust_font_size(title)
        title_w, title_h = title_font.getsize(title)
        title_x = int((self._display.WIDTH - title_w) / 2)
        title_y = 0 + self._padding
        self._draw.text((title_x, title_y), title, self._display.YELLOW,
                        font=title_font)
        if incident:
            mark_w, mark_h = title_font.getsize(INCIDENT_MARK)
            mark_x = self._display.WIDTH - mark_w - self._padding
            mark_y = 0 + self._padding
            self._draw.text((mark_x, mark_y), INCIDENT_MARK,
                            self._display.YELLOW,
                            font=title_font)

    def _draw_arrivals(self, arrivals: List[Arrival]):
        pass

    def show_arrivals(self, arrivals: ArrivalInfo):
        self._init_canvas()
        self._draw_background()
        self._draw_title(unidecode(arrivals['stop_name']), arrivals['incident'])
        self._display.set_image(self._img)
        self._display.show()

    def wait_for_window_close(self):
        self._display.wait_for_window_close()
