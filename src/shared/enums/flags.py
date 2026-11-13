
from enum import Enum, IntEnum, F
from typing import SupportsInt


def has_flag(value: int, flags: int) -> bool:
    """
    Example:
    ```python
    LEFT 	= 1 << 0 # 1 - 0b0001
    TOP 	= 1 << 1 # 2 - 0b0010
    RIGHT	= 1 << 2 # 4 - 0b0100
    BOTTOM	= 1 << 3 # 8 - 0b1000
    HORIZONTAL 	= LEFT | RIGHT # 5  - 0b0101
    VERTICAL 	= TOP | BOTTOM # 10 - 0b1010
    ALL 		= HORIZONTAL | VERTICAL # 15 - 0b1111

    side = HORIZONTAL
    if has_flag(side, LEFT): ... # true
    if has_flag(side, TOP):  ... # false

    side = TOP | LEFT
    if has_flag(side, HORIZONTAL): ... # false
    if has_flag(side, LEFT | BOTTOM): ... # false
    if has_flag(side, LEFT): ... # true
    ```
    """
    return (value & flags) == flags

class FlagsMixin:
    def has_flag(self: SupportsInt, flags: int):
        """
        Example:
        ```python
        class Side(FlagsMixin, IntEnum):
            LEFT 	= 1 << 0 # 1 - 0b0001
            TOP 	= 1 << 1 # 2 - 0b0010
            RIGHT	= 1 << 2 # 4 - 0b0100
            BOTTOM	= 1 << 3 # 8 - 0b1000
            HORIZONTAL 	= LEFT | RIGHT # 5  - 0b0101
            VERTICAL 	= TOP | BOTTOM # 10 - 0b1010
            ALL 		= HORIZONTAL | VERTICAL # 15 - 0b1111

        side = Side.HORIZONTAL
        if has_flag(side, Side.LEFT): ... # true
        if has_flag(side, Side.TOP):  ... # false

        side = Side.TOP | Side.LEFT
        if has_flag(side, Side.HORIZONTAL): ... # false
        if has_flag(side, Side.LEFT | Side.BOTTOM): ... # false
        if has_flag(side, Side.LEFT): ... # true
        ```
        """
        return has_flag(int(self), flags)
