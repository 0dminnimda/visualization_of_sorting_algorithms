from dataclasses import dataclass
from typing import List, MutableSequence, Tuple, Type, Union

import numpy as np
import pygame as pg

from .game_loop import Color, Position, PygamePainter
from .recorded_list import (
    AppendOp,
    ClearOp,
    CreateOp,
    GetOp,
    Item,
    Operation,
    RecordedList,
    SetOp,
)
from .sorts import Sort


@dataclass
class ColoredItem:
    value: Item
    color: Union[str, Color]


class SortVisualizer(PygamePainter):
    def setup_grid(self, rows: int, columns: int, x_offset: int, y_offset: int) -> None:
        self.x_offset = x_offset
        self.rows = rows
        self.delta_x = self.width / self.rows
        self.width_x = self.delta_x - self.x_offset
        margin_x = self.width - self.delta_x * self.rows
        self.start_x = margin_x / 2
        if self.delta_x < 1:
            self.line_mode = True

        self.y_offset = y_offset
        self.columns = columns
        self.delta_y = self.height / self.columns
        self.width_y = self.delta_y - self.y_offset
        margin_y = self.height - self.delta_y * self.columns
        self.start_y = margin_y / 2
        assert self.delta_y > 1

        max_item = max(self.arrays[0], key=lambda i: i.value).value
        self.sizes = {}
        for item in self.arrays[0]:
            size = self.width_y * item.value / max_item
            self.sizes[item.value] = (self.width_y - size, size)

    def setup(  # type: ignore
        self,
        sort: Type[Sort],
        array: MutableSequence[Item],
        ops_per_frame: int = 1,
        delay: int = 0,
    ):
        self.arrays: List[List[ColoredItem]] = []
        self.arrays.append([ColoredItem(i, "white") for i in array])
        self.current_array = self.arrays[0]

        offset = 0
        self.line_mode = False
        self.setup_grid(len(array), 1 + sort.num_of_auxiliary_arrays, offset, offset)

        self.history = sort(RecordedList(array)).run().array.history
        assert self.history.pop(0) == CreateOp(0)

        self.ops_per_frame = ops_per_frame
        assert delay == 0, "'delay' is not implemented yet"
        self.delay = delay

        # pg.mixer.music.load(filename)
        # pg.mixer.music.set_volume(1)
        # pg.mixer.music.play()

    def is_exit_event(self, event: pg.event.Event) -> bool:
        if event.type == pg.QUIT:
            return True
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
            return True
        return False

    def on_event(self, event) -> None:
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            self.pause()

    def apply_operation(self, op: Operation) -> None:
        if isinstance(op, GetOp):
            self.arrays[op.array_index][op.key].color = "yellow"
        elif isinstance(op, SetOp):
            self.arrays[op.array_index][op.key] = ColoredItem(op.value, "blue")
        elif isinstance(op, CreateOp):
            self.arrays.append([])
            assert op.array_index == len(self.arrays) - 1
        elif isinstance(op, AppendOp):
            self.arrays[op.array_index].append(ColoredItem(op.value, "white"))
        elif isinstance(op, ClearOp):
            self.arrays[op.array_index].clear()
        else:
            raise ValueError(f"unknown 'op' type {op.__class__.__name__}")

    def _make_values(
        self, value: Item, row: int, column: int
    ) -> Tuple[float, float, float, float]:
        start_y, width_y = self.sizes[value]
        return (
            self.start_x + self.delta_x * row,
            start_y + self.delta_y * column,
            self.width_x,
            width_y,
        )

    def make_line(
        self, value: Item, row: int, column: int
    ) -> Tuple[Position, Position]:
        x, y, w, h = self._make_values(value, row, column)
        return (x, y), (x, y + h)

    def make_rect(self, value: Item, row: int, column: int) -> pg.Rect:
        return pg.Rect(*self._make_values(value, row, column))

    def draw(self) -> None:
        self.fill()

        for column in range(len(self.arrays)):
            array = self.arrays[column]
            assert self.rows >= len(array)
            for row in range(len(array)):
                item = array[row]
                self.set_color(item.color)
                item.color = "white"
                if self.line_mode:
                    self.line(*self.make_line(item.value, row, column))
                else:
                    self.rect(self.make_rect(item.value, row, column))

        for _ in range(self.ops_per_frame):
            if self.history:
                self.apply_operation(self.history.pop(0))
