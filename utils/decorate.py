from __future__ import annotations

from datetime import datetime
from pathlib import Path
import json
import sys
import functools
import typing

if typing.TYPE_CHECKING:
    from .typeshed import *

from .common import console
from .pathing import LOG_DIR


def _fmt_time(dt: datetime) -> str:
    return dt.strftime("%I:%M:%S %p")


def _diff_time(start: datetime, end: datetime | None = None) -> float:
    return ((end or datetime.now()) - start).total_seconds()


def timings(
    *,
    disp_name: str | None = None,
    strip_prefix: str = "_",
):
    def decorator[**P, T](func: Callable[P, T]) -> Callable[P, T]:
        nonlocal disp_name

        disp_name = disp_name or chr(32).join(
            x.strip().capitalize() for x in func.__name__.lstrip(strip_prefix).split("_")
        )

        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                started_at = datetime.now()
                console.log(f"[{disp_name}]: started at {_fmt_time(started_at)}")

                result = func(*args, **kwargs)

                ended_at = datetime.now()
                console.log(f"[{disp_name}]: completed at {_fmt_time(ended_at)}")

                duration = _diff_time(started_at, ended_at)
                if duration > 1:
                    console.log(f"[{disp_name}]: took {duration} seconds")

                return result
            except Exception as e:
                console.error(f"An unhandled exception occured in {func.__name__}", e)
                raise

        return wrapper

    return decorator


def retry(
    *,
    max_retries: int,
    before_retry: Callable[[], Any] | None = None,
):
    attempts = 0

    def decorator[**P, T](func: Callable[P, T]) -> Callable[P, T]:
        @functools.wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            try:
                return func(*args, **kwargs)
            except Exception as e:
                nonlocal attempts

                if attempts <= max_retries:
                    attempts += 1
                    before_retry and before_retry()
                    return wrapper(*args, **kwargs)

                console.error(exception=e)
                raise

        return wrapper

    return decorator


def get_dump_file() -> Path:
    return LOG_DIR / f"dump_{datetime.now().timestamp()}.log"


def is_serializable(x: object) -> bool:
    return hasattr(x, "__str__") or hasattr(x, "__repr__")


class dumplocals[**P, T]:
    """
    A decorator class that captures local variables of a decorated function
    if it raises an exception.
    """

    def __init__(self, func: Callable[P, T]):
        """
        Initializes the decorator with the function to be decorated.
        """
        self._locals = {}
        self.func = func

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> T:
        """
        The main decorator logic. Sets up a tracer and calls the function.
        """
        # We need to save the original profile function to restore it later
        original_profile_func = sys.getprofile()

        def tracer(frame, event, arg):
            """
            The tracer function that captures locals on return or exception.
            """
            # Check for the frame of the decorated function itself
            if frame.f_code is self.func.__code__:
                if event == "return":
                    # For a normal return, capture the locals from the frame
                    self._locals = frame.f_locals.copy()
                elif event == "exception":
                    # When an exception is raised, capture the locals from the frame
                    self._locals = frame.f_locals.copy()

            # This is important to not break other profilers
            if original_profile_func:
                original_profile_func(frame, event, arg)

        sys.setprofile(tracer)
        try:
            res = self.func(*args, **kwargs)
        except Exception as e:
            self.write_locals()
            raise SystemExit from e
        finally:
            sys.setprofile(original_profile_func)
            self.clear_locals()

        return res

    def clear_locals(self):
        """
        Clears the captured local variables.
        """
        self._locals = {}

    def write_locals(self, file: Path | None = None):
        file = file or get_dump_file()
        file.write_text(
            json.dumps(
                self.locals,
                indent=4,
                skipkeys=True,
                default=str,
                sort_keys=True,
            )
        )
        console.log(f"Locals dumped to '{file}'")

    @property
    def locals(self):
        """
        Returns the captured local variables.
        """
        return self._locals
