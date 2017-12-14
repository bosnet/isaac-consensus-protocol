from enum import Enum


class StateKind(Enum):
    NONE = 0
    INIT = 1
    SIGN = 2
    ACCEPT = 3
    ALLCONFIRM = 4
