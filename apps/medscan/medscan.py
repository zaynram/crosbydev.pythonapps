from __future__ import annotations
from argparse import Namespace
from utils.common import console
from .preprocess import Preprocessor
from .analyze import Analyzer


class Medscan(Namespace, Preprocessor, Analyzer):
    command: str

    def invoke(self) -> None:
        console.FILE.write_text("")
        func = self._debug if self.debug else getattr(self, self.command, None)
        if not callable(func):
            raise TypeError("Invalid command.")
        func.__call__(self)

    def _debug(self) -> None:
        console.debug(**{key: val for key, val in self.__dict__.items() if not callable(val)})
