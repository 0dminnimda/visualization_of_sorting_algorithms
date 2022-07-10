from dataclasses import dataclass, field
from shutil import SpecialFileError
from time import perf_counter
from typing import Iterable, List, Optional, Sized


Key = int
Item = int


@dataclass
class Operation:
    array_index: int
    time: float = field(default_factory=perf_counter, init=False, compare=False)


@dataclass
class GetOp(Operation):
    key: Key


@dataclass
class SetOp(Operation):
    key: Key
    value: Item


@dataclass
class CreateOp(Operation):
    pass


@dataclass
class AppendOp(Operation):
    value: Item


@dataclass
class ClearOp(Operation):
    pass


def slice_to_range(s: slice, sized: Sized) -> range:
    start = s.start
    if start is None:
        start = 0

    stop = s.stop
    if stop is None:
        stop = len(sized)

    step = s.step
    if step is None:
        step = 1

    return range(start, stop, step)


History = List[Operation]


class RecordedList(list):
    array_index: int
    number_of_children: int
    history: History

    def __init__(
        self,
        iterable: Iterable[Item] = tuple(),
        parent: Optional["RecordedList"] = None,
    ):
        super().__init__(iterable)

        if parent is None:
            self.history = []
            self.array_index = 0
        else:
            self.history = parent.history
            self.array_index = parent.add_child(self)

        self.history.append(CreateOp(self.array_index))
        self.number_of_children = 0

    def add_child(self, child: "RecordedList") -> int:
        self.number_of_children += 1
        return self.number_of_children

    # useless to explicitly set the types
    # as well as it makes things worse here
    def __getitem__(self, key):
        if isinstance(key, slice):
            self.history.extend(
                (GetOp(self.array_index, k) for k in slice_to_range(key, self))
            )
        elif isinstance(key, int):
            self.history.append(GetOp(self.array_index, key))
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            self.history.extend(
                (
                    SetOp(self.array_index, k, v)
                    for k, v in zip(slice_to_range(key, self), value)
                )
            )
        elif isinstance(key, int):
            self.history.append(SetOp(self.array_index, key, value))
        return super().__setitem__(key, value)

    def append(self, value) -> None:
        self.history.append(AppendOp(self.array_index, value))
        return super().append(value)

    def clear(self) -> None:
        self.history.append(ClearOp(self.array_index))
        return super().clear()
