from typing import List

from PIL import Image, ImageFont, ImageDraw
from PIL.ImageFont import FreeTypeFont
from font_connection_iii import ConnectionIII
from unidecode import unidecode

from model import ArrivalInfo, Arrival

INCIDENT_MARK = '*'
MAX_TITLE_SIZE = 20
MAX_CONTENT_SIZE = 20


class ArrivalDisplay:

    def __init__(self, display_type: str, color: str, mock=False):
        self._is_mocked = mock
        self._init_display(color, mock, display_type)
        self._init_canvas()
        self._titleHash = 0
        self._content_hash = 0

    def _init_display(self, color: str, mock=False, display_type='phat'):
        if mock:
            from inky import InkyMockPHAT as InkyPHAT
            from inky import InkyMockWHAT as InkyWHAT
        else:
            from inky import InkyPHAT
            from inky import InkyWHAT
        if display_type == 'phat':
            self._display = InkyPHAT(color)
            self._scale_size = 1.0
            self._padding = 2
        elif display_type == 'what':
            self._display = InkyWHAT(color)
            self._scale_size = 2.20
            self._padding = 15
        self._display.set_border(self._display.BLACK)

    def _init_canvas(self):
        """must be called after _init_display"""
        img = Image.new("P", (self._display.WIDTH, self._display.HEIGHT))
        self._img = img
        self._draw = ImageDraw.Draw(img)

    def _draw_background(self, height: int, offset_y=0):
        for y in range(offset_y, offset_y + height):
            for x in range(0, self._display.width):
                self._img.putpixel((x, y), self._display.BLACK)

    def _adjust_font_size(self, text: str, max_size: int) -> FreeTypeFont:
        font_size = max_size
        while True:
            font = ImageFont.truetype(ConnectionIII,
                                      int(font_size * self._scale_size))
            title_w, title_h = font.getsize(text)
            if title_w + self._padding > self._display.WIDTH:
                font_size -= 1
            else:
                return font

    def _draw_title(self, title: str, incident: bool) -> int:
        new_title = f'{title}/{incident}'
        title_font = self._adjust_font_size(title, MAX_TITLE_SIZE)
        title_w, title_h = title_font.getsize(title)
        title_x = int((self._display.WIDTH - title_w) / 2)
        title_y = 0 + self._padding
        if hash(new_title) != self._titleHash:
            self._draw_background(title_h + self._padding)
            self._draw.text(xy=(title_x, title_y), text=title,
                            fill=self._display.YELLOW, font=title_font)
            if incident:
                mark_w, mark_h = title_font.getsize(INCIDENT_MARK)
                mark_x = self._display.WIDTH - mark_w - self._padding
                mark_y = 0 + self._padding
                self._draw.text(xy=(mark_x, mark_y), text=INCIDENT_MARK,
                                fill=self._display.YELLOW, font=title_font)
        self._titleHash = hash(new_title)
        return title_h + self._padding

    def _draw_arrivals(self, arrivals: List[Arrival], offset_y=0):
        if hash(tuple(arrivals)) == self._content_hash:
            return
        self._draw_background(self._display.height - offset_y, offset_y)

        font = None
        font_size = MAX_CONTENT_SIZE
        max_ln_w, max_dst_w, max_time_w = 0, 0, 0
        max_ln_h, max_dst_h, max_time_h = 0, 0, 0
        ln_padding_x, ln_padding_y = 10, 5
        while True:
            font = ImageFont.truetype(ConnectionIII,
                                      int(font_size * self._scale_size))
            for arrival in arrivals:
                max_ln_w, max_ln_h = font.getsize(arrival.line)
                max_dst_w, max_dst_h = font.getsize(arrival.destination)
                max_time_w, max_time_h = font.getsize(arrival.fmt_est())
            max_w = 2 * self._padding \
                + 2 * ln_padding_x \
                + max_dst_w + max_ln_w + max_time_w
            max_h = self._padding + offset_y \
                + len(arrivals) * (max_time_h + ln_padding_y)
            if max_w > self._display.width or max_h > self._display.height:
                font_size -= 1
            else:
                break

        x, y = self._padding, offset_y
        for arrival in arrivals:
            self._draw.text(
                xy=(x, y), fill=self._display.YELLOW,
                text=arrival.line, font=font)
            x += max_ln_w + ln_padding_x
            self._draw.text(
                xy=(x, y), fill=self._display.YELLOW,
                text=arrival.destination, font=font)
            x += max_dst_w + ln_padding_x
            self._draw.text(
                xy=(x, y), fill=self._display.YELLOW,
                text=arrival.fmt_est(), font=font)
            x = self._padding
            y += font.getsize(arrival.line)[1] + ln_padding_y
        self._content_hash = hash(tuple(arrivals))

    def show_arrivals(self, arrivals: ArrivalInfo):
        self._init_canvas()
        content_offset_y = self._draw_title(unidecode(arrivals.stop_name),
                                            arrivals.incident)
        self._draw_arrivals(arrivals.arrivals, content_offset_y)
        self._display.set_image(self._img)
        self._display.show()

    def wait_for_window_close(self):
        if self._is_mocked:
            self._display.wait_for_window_close()
