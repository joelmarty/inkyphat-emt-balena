from PIL import Image, ImageFont, ImageDraw
from font_connection_iii import ConnectionIII
from unidecode import unidecode

from inky_emt.domain.model import ArrivalInfo


class ArrivalDisplay:

    def __init__(self, display_type: str, color: str, mock=False):
        self._init_display(color, mock, display_type)
        self._init_canvas()
        self._init_fonts()
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
            self._padding = 0
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

    def _init_fonts(self):
        self._font = ImageFont.truetype(ConnectionIII,
                                        int(22 * self._scale_size))

    def _draw_title(self, title: str, incident: bool):
        title_w, title_h = self._font.getsize(title)
        title_x = int((self._display.WIDTH - title_w) / 2)
        title_y = 0 + self._padding
        self._draw.text((title_x, title_y), title, self._display.YELLOW,
                        font=self._font)
        if incident:
            mark_w, mark_h = self._font.getsize('!')
            mark_x = self._display.WIDTH - mark_w - self._padding
            mark_y = 0 + self._padding
            self._draw.text((mark_x, mark_y), '!', self._display.YELLOW,
                            font=self._font)

    def set_title(self, line: str, destination: str, incident: bool):
        normalized_dest = unidecode(destination)
        title = line + " " + normalized_dest
        self._draw_title(title, incident)

    def set_arrivals(self, arrivals: ArrivalInfo):
        pass

    def refresh(self):
        self._display.set_image(self._img)
        self._display.show()
        self._init_canvas()

    def wait_for_window_close(self):
        self._display.wait_for_window_close()
