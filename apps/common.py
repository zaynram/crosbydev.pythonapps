from __future__ import annotations

import json
import sys
import typing

# Make wx optional
try:
    import wx
    WX_AVAILABLE = True
except ImportError:
    WX_AVAILABLE = False

from ramda_py.decor import *
from ramda_py.util import *
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from datetime import date
    from ramda_py.types import *

DATA_DIR = rootpath(__file__, "data", mkdir=True, resolve=True).as_posix()


class argtype:
    @staticmethod
    def datestring(value) -> date:
        if not value:
            raise TypeError("Date is a required field.")

        if isinstance(value, date):
            return value

        try:
            return date.fromisoformat(value)
        except Exception:
            raise TypeError("Date must be in ISO format.")

    @staticmethod
    def boolstring(value) -> bool:
        if isinstance(value, str):
            return str(value) == "True"
        raise TypeError("Must be either 'True' or 'False'.")

    @staticmethod
    def nowhitespaces(value) -> str:
        if isinstance(value, str) and " " not in value.strip():
            return value.strip()
        raise TypeError("Must be a string not containing any whitespaces.")

    @staticmethod
    def integerlist(value) -> list[int]:
        try:
            return [int(n.strip()) for n in str(value).split(",")]
        except Exception:
            raise TypeError("All values in the list must be integers.")


class console:
    NEWLINE = typing.final(chr(13) + chr(10) if sys.platform == "win32" else chr(10))
    FILE = typing.final(rootpath(__file__, "logs", mkdir=True) / "latest-execution.log")
    WHITELIST = typing.final(["progress"])
    BLACKLIST = typing.final([
        "mupdf error",
        "image too small",
        "line cannot be recognized",
        "configuration",
        "file_info",
        "locals dumped",
    ])

    @classmethod
    def debug(cls, **kwds: object) -> None:
        for k, v in kwds.items():
            cls.log(f"[debug] {k}", f"\tvalue: {v}", f"\ttype: {type(v)}")

    @classmethod
    def json(
        cls,
        key: str | None = None,
        obj: JSONDict | None = None,
        *,
        indent: int = 4,
        **kwds: JSONSerializable,
    ) -> None:
        obj = {**(obj or {}), **kwds}
        data: JSONDict = obj if not key else {key: obj}
        cls.log(json.dumps(obj=data, indent=indent))

    @classmethod
    def log(cls, *lines: object) -> None:
        text = " ".join(str(line).lower() for line in lines)
        if all(item not in text for item in cls.WHITELIST) or any(item in text for item in cls.BLACKLIST):
            with cls.FILE.open("a+t", encoding="utf-8") as f:
                print(*lines, sep=cls.NEWLINE, file=f)
        else:
            print(*lines, sep=cls.NEWLINE, file=sys.stdout, flush=True)

    @staticmethod
    def error(
        *lines: object,
        exception: Exception | type[Exception] | None = None,
        fatal: bool = False,
    ) -> None:
        exception and console.log(exception)
        lines and console.log(lines)
        fatal and sys.exit(1)

    @staticmethod
    def confirm(prompt: str) -> bool:
        dialogue = wx.MessageDialog(
            parent=None,
            message=prompt,
            caption="Confirmation",
            style=wx.YES_NO | wx.ICON_QUESTION,
        )
        choice = dialogue.ShowModal()
        dialogue.Destroy()
        return choice == wx.ID_YES


class track[I]:
    GLOBAL_TOTAL: typing.ClassVar[int] = 100

    _total: int

    @property
    def total(self) -> int:
        return getattr(self, "_total", self.GLOBAL_TOTAL)

    @total.setter
    def total(self, value: int | None) -> None:
        self._total = value or self.GLOBAL_TOTAL

    iterator: Iterator[I]
    description: str
    current: int = 0

    @property
    def progress(self) -> str:
        return f"progress: {self.current}/{self.total}\n"

    def __init__(self, iterable: Iter[I], desc: str, total: int | None = None) -> None:
        self.total = total if not isinstance(iterable, typing.Sized) else len(iterable)
        self.description = desc
        self.iterator = iter(iterable)

    def _write_progress(
        self,
        *,
        advance: int | None = None,
        complete: bool = False,
    ) -> None:
        if complete:
            self.current = 0
            self.total = 100
        elif self.current == self.total:
            self.total += 1
        elif advance:
            self.current += advance
        console.log(self.progress)

    def __iter__(self) -> Generator[I]:
        console.log(self.description)
        try:
            while True:
                yield next(self.iterator)
                self._write_progress(advance=1)
        except StopIteration:
            self._write_progress(complete=True)
            del self.iterator, self.current, self._total, self.description
