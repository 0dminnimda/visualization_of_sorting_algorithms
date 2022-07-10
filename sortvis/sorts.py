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
