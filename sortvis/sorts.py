from dataclasses import dataclass
from typing import Tuple
from .recorded_list import Key, RecordedList


__all__ = [
    "Sort",
    "CocktailShakerSort",
    "BubbleSort",
    "MergeSort",
]


@dataclass
class Sort:
    array: RecordedList
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


class BubbleSort(CocktailShakerSort):
    def run(self) -> Sort:
        self.start = 0
        self.end = len(self.array)

        while self.make_iteration(False):
            pass

        return self


class MergeSort(Sort):
    auxiliary_array: RecordedList
    num_of_auxiliary_arrays: int = 1

    def sort_array(self, start: Key, end: Key) -> Tuple[int, int]:
        length = end - start
        if length < 1:
            assert False, "Unreachable"
        if length == 1:
            return start, end
        if length == 2:
            a, b = self.array[start:end]
            if a > b:
                self.array[start:end] = [b, a]
            else:
                self.array[start:end] = [a, b]
            return start, end
        mid = (end - start) // 2 + start
        s1, e1 = self.sort_array(start, mid)
        s2, e2 = self.sort_array(mid, end)
        a, b = self.array[s1], self.array[s2]
        while 1:
            if a > b:
                self.auxiliary_array.append(b)
                s2 += 1
                if not (s2 < e2):
                    break
                b = self.array[s2]
            else:
                self.auxiliary_array.append(a)
                s1 += 1
                if not (s1 < e1):
                    break
                a = self.array[s1]
        if s1 < e1:
            assert s2 == e2
            for i in range(s1, e1):
                self.auxiliary_array.append(self.array[i])
        elif s2 < e2:
            assert s1 == e1
            for i in range(s2, e2):
                self.auxiliary_array.append(self.array[i])
        else:
            assert False, f"Unreachable: {s1}, {e1}, {s2}, {e2}"
        for i in range(start, end):
            self.array[i] = self.auxiliary_array[i - start]
        self.auxiliary_array.clear()
        return start, end

    def run(self) -> Sort:
        self.auxiliary_array = RecordedList(parent=self.array)
        self.sort_array(0, len(self.array))
        return self
