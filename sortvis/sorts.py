from dataclasses import dataclass
from typing import Tuple
from .recorded_list import Key, RecordedList


@dataclass
class Sort:
    array: RecordedList
    # auxiliary_arrays: List[RecordedList] = field(default_factory=list)
    num_of_auxiliary_arrays: int = 0

    def run(self) -> "Sort":
        raise NotImplementedError


class CocktailShakerSort(Sort):
    start: Key
    end: Key

    def make_iteration(self, reversed: bool) -> bool:
        result = False

        if reversed:
            change = 1
            prev = self.array[self.end - 1]
            indices = range(self.start, self.end - 1)[::-1]
        else:
            change = -1
            prev = self.array[self.start]
            indices = range(self.start + 1, self.end)

        for i in indices:
            current = self.array[i]
            swap = prev > current
            if reversed:
                swap = not swap

            if swap:
                self.array[i + change] = current
                self.array[i] = prev
                result = True
                if reversed:
                    self.start = i
                else:
                    self.end = i
            else:
                prev = current

        return result

    def run(self) -> Sort:
        self.start = 0
        self.end = len(self.array)

        reversed = True
        while self.make_iteration(reversed):
            reversed = not reversed

        return self
