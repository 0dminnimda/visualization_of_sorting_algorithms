from contextlib import contextmanager
from typing import Any, Generator, List, Optional, Sequence, Tuple, Union
import pygame as pg
from pygame import draw


Color = Union[Tuple[int, int, int], Tuple[int, int, int, int]]
InColor = Union[str, Color]
Position = Tuple[float, float]
Rect = Union[pg.Rect, Tuple[int, int, int, int]]  # TODO: not complete


class GameLoop:
    running: bool

    def setup(self, *args: Any, **kwargs: Any) -> None:
        pass

    def tick(self) -> None:
        pass

    def is_exit_event(self, event: pg.event.Event) -> bool:
        return False

    def on_event(self, event: pg.event.Event) -> None:
        pass

    def running_check(self) -> None:
        pass

    def draw(self) -> None:
        pass

    def update(self) -> None:
        pass

    def finish(self) -> None:
        pass

    def run(self, *args: Any, **kwargs: Any) -> None:
        self.running = True
        self.setup(*args, **kwargs)

        while self.running:
            self.tick()

            for event in pg.event.get():
                if self.is_exit_event(event):
                    self.running = False
                else:
                    self.on_event(event)

            self.running_check()

            if not self.running:
                break

            self.draw()

            self.update()

        self.finish()


class PygamePainter(GameLoop):
    def __init__(
        self, size: Tuple[int, int] = (0, 0), name: Optional[str] = None
    ) -> None:
        pg.init()

        self._init_window(size, name)

        self.clock = pg.time.Clock()

        self.colors = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "white": (255, 255, 255),
            "black": (0, 0, 0),
            "gray": (127, 127, 127),
            "yellow": (255, 255, 0),
            "lblue": (0, 255, 255),
            "purple": (255, 0, 255),
        }

        self.set_color("white")

        self.fonts: List[pg.font.Font] = []

        self._init_paint_loop()

    def _init_window(self, size: Tuple[int, int], name: Optional[str]) -> None:
        # create the resizable window
        self.window = pg.display.set_mode(size, pg.RESIZABLE)

        self.size = self.window.get_size()

        # create the surface with the alpha channel
        self.surface = pg.Surface(self.size, pg.SRCALPHA)

        if not isinstance(name, str):
            name = f"Pygame {self.__class__.__name__} Window"

        pg.display.set_caption(name)  # set the window name
        self._display_info = pg.display.Info()

    def _init_paint_loop(self) -> None:
        self.framerate = 0

    def tick(self) -> None:
        if self.framerate > 0:
            self.clock.tick(self.framerate)

    def update(self) -> None:
        locked = self.surface.get_locked()
        if locked:
            self.surface.unlock()

        self.window.blit(self.surface, (0, 0))
        # pg.display.update()
        pg.display.flip()

        if locked:
            self.surface.lock()

    def to_color(self, name: InColor) -> Color:
        if isinstance(name, str):
            color = self.colors
            return color[name.lower()]
        else:
            return name

    def set_color(self, color: InColor) -> None:
        self.color = self.to_color(color)

    @contextmanager
    def set_temp_color(self, color: InColor) -> Generator[None, None, None]:
        prev = self.color
        self.color = self.to_color(color)
        yield
        self.color = prev

    @property
    def width(self) -> int:
        """return width of the window"""
        return self.size[0]

    @property
    def height(self) -> int:
        """return height of the window"""
        return self.size[1]

    @property
    def center(self) -> Tuple[float, float]:
        """return center point of the window"""
        return (self.width / 2, self.height / 2)

    def _draw(self, func, *args, **kwargs) -> None:
        func(self.surface, self.color, *args, **kwargs)

    def circle(self, position: Position, radius=1, width=0) -> None:
        if width > radius:
            radius = width
        self._draw(draw.circle, position, radius, width)

    def line(
        self,
        start: Position,
        end: Position,
        width: int = 1,
        blend: Optional[int] = None,
    ) -> None:
        if blend is None:
            self._draw(draw.line, start, end, width)
        else:
            self._draw(draw.aaline, start, end, blend)

    def polygon(self, positions: Sequence[Position], width=0) -> None:
        self._draw(draw.polygon, positions, width)

    def rect(self, rect: Rect, width: int = 0) -> None:
        self._draw(draw.rect, rect, width)

    def ellipse(self, rect: Rect, width: int = 1) -> None:
        self._draw(draw.ellipse, rect, width)

    def arc(
        self, rect: Rect, start_argle: float, end_angle: float, width: int = 1
    ) -> None:
        self._draw(draw.arc, rect, start_argle, end_angle, width)

    def font_init(self, font_size: int, font_name: str = "arial") -> int:
        self.fonts.append(pg.font.SysFont(font_name, font_size))
        return len(self.fonts) - 1

    def text(
        self,
        font_id: int,
        text: Any,
        point: Tuple[float, float],
        text_color: InColor = "white",
        fill_color: Optional[InColor] = None,
        rect_width: Optional[int] = None,
        rect_color: InColor = "black",
    ) -> None:
        chars = str(text)
        font = self.fonts[font_id]

        if fill_color is not None:
            fill_color = self.to_color(fill_color)
        rendered_text = font.render(chars, True, self.to_color(text_color), fill_color)

        if rect_width is not None:
            size = font.size(chars)
            rect = pg.Rect(point[0], point[1], size[0] * 1.1, size[1] * 1.1)
            with self.set_temp_color(rect_color):
                self.rect(rect, rect_width)
            self.blit(rendered_text, (point[0] + 5, point[1]))
        else:
            self.blit(rendered_text, point)

    def blit(self, surface: pg.surface.Surface, position: Tuple[float, float]) -> None:
        self.surface.blit(surface, position)

    def fill(self, color: InColor = "black") -> None:
        self.surface.fill(self.to_color(color))

    def display_info_changed(self) -> bool:
        return self._display_info != pg.display.Info()

    def pause(self) -> bool:
        while 1:
            event = pg.event.wait()
            if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                return True
            elif event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return False
        assert False, "Unreachable"
