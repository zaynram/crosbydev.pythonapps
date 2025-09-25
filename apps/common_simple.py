"""
Simplified common utilities for Doculyze without heavy dependencies.
"""
from __future__ import annotations

import json
import sys
import typing
from pathlib import Path
from typing import TYPE_CHECKING, Any, Dict, Generator, Optional, Callable
import time
import datetime as dt

if TYPE_CHECKING:
    from datetime import date


def rootpath(file_path: str, *parts: str, mkdir: bool = False, resolve: bool = False) -> Path:
    """Get root path relative to a file."""
    path = Path(file_path).parent
    for part in parts:
        path = path / part
    
    if mkdir and not path.exists():
        path.mkdir(parents=True, exist_ok=True)
    
    if resolve:
        path = path.resolve()
    
    return path


DATA_DIR = rootpath(__file__, "data", mkdir=True, resolve=True).as_posix()


class argtype:
    @staticmethod
    def datestring(value) -> date:
        if not value:
            raise TypeError("Date is a required field.")

        if isinstance(value, date):
            return value

        try:
            from datetime import date
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
        """Debug output."""
        print("DEBUG:", kwds)

    @classmethod
    def json(
        cls,
        key: str | None = None,
        obj: Dict[str, Any] | None = None,
        *,
        indent: int = 4,
        **kwds: Any,
    ) -> None:
        """JSON output."""
        data = obj if obj is not None else kwds
        if key:
            data = {key: data}
        print(json.dumps(data, indent=indent))

    @classmethod
    def log(cls, *lines: object) -> None:
        """Log messages."""
        for line in lines:
            print(f"LOG: {line}")

    @staticmethod
    def error(
        *lines: object,
        exception: Exception | type[Exception] | None = None,
        fatal: bool = False,
    ) -> None:
        """Error messages."""
        for line in lines:
            print(f"ERROR: {line}", file=sys.stderr)
        if exception:
            print(f"EXCEPTION: {exception}", file=sys.stderr)
        if fatal:
            sys.exit(1)

    @staticmethod
    def confirm(prompt: str) -> bool:
        """Confirmation prompt."""
        response = input(f"{prompt} (y/N): ").strip().lower()
        return response in ['y', 'yes']


class track:
    """Simple progress tracker."""
    
    def __init__(self, iterable, desc: str = "", total: Optional[int] = None):
        self.iterable = iterable
        self.desc = desc
        self.total = total or (len(iterable) if hasattr(iterable, '__len__') else None)
        self.current = 0
        
    def __iter__(self):
        console.log(f"Starting: {self.desc}")
        start_time = time.time()
        
        for item in self.iterable:
            self.current += 1
            if self.total:
                progress = f"({self.current}/{self.total})"
            else:
                progress = f"({self.current})"
            
            print(f"Progress {progress}: {self.desc}")
            yield item
        
        elapsed = time.time() - start_time
        console.log(f"Completed: {self.desc} in {elapsed:.2f}s")


def retry(max_retries: int = 3):
    """Simple retry decorator."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            last_exception = None
            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt < max_retries - 1:
                        console.log(f"Retry {attempt + 1}/{max_retries} for {func.__name__}")
                        time.sleep(1)  # Brief delay between retries
                    continue
            raise last_exception
        return wrapper
    return decorator


def timings():
    """Simple timing decorator."""
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start_time = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start_time
            console.log(f"{func.__name__} completed in {elapsed:.2f}s")
            return result
        return wrapper
    return decorator