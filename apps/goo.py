from __future__ import annotations

from gooey import Gooey, GooeyParser

from functools import wraps
from typing import TYPE_CHECKING, final

if TYPE_CHECKING:
    from argparse import ArgumentParser
    from ramda_py.types import *

DEFAULT_GOOEY_ARGS = final({
    "header_show_help": True,
    "hide_progress_msg": True,
    "timing_options": {
        "show_time_remaining": True,
        "hide_time_remaining_on_complete": True,
    },
    "progress_regex": r"^progress: (?P<current>\d+)/(?P<total>\d+)$",
    "progress_expr": "current / total * 100",
    "default_size": (1200, 600),
    "return_to_config": False,
    "show_failure_modal": True,
    "tabbed_groups": True,
    "show_restart_button": False,
    "run_validation": True,
    "group_by_type": True,
    "show_preview_warning": False,
})


def gooify[**P, T](
    name: str,
    desc: str = "",
    *,
    basic: bool = False,
    **kwds: object,
) -> Callable[[Callable[P, T]], Callable[P, T]]:
    gooey_dict: dict[str, Any] = DEFAULT_GOOEY_ARGS.copy()
    gooey_dict.update({
        **kwds,
        "advanced": not basic,
        "program_name": name,
        "program_description": desc,
    })

    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        @wraps(func)
        @Gooey(**gooey_dict)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
            return func(*args, **kwargs)

        return wrapper

    return decorator


def gooparse(desc: str) -> GooeyParser | ArgumentParser:
    return GooeyParser(description=desc)
