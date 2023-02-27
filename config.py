from asyncio.windows_events import NULL
import enum
import json
from logging import WARNING
from types import SimpleNamespace

class LogType(enum.Enum):
    WARNING = 3
    ERROR   = 2
    INFO    = 1

class TaskType(enum.Enum):
    CALL    = 'call'
    EMAIL   = 'email'
    MEETING = 'meeting'
    TASK    = 'task'
    LUNCH   = 'lunch'
    VISIT   = 'visit'

class Config():
    
    def __init__(self) -> None:
        self.cfg = NULL
        return None

    def open(self) -> None:
        f = open("config.json")
        self.cfg = json.loads(f.read(),object_hook=lambda d: SimpleNamespace(**d))

    def get(self) -> str:
        return self.cfg