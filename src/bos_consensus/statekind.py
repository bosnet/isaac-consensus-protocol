from enum import Enum


class StateKind(Enum):
    INIT = 1
    SIGN = 2
    ACCEPT = 3
    ALLCONFIRM = 4
