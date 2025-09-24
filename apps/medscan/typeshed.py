# ruff: noqa: F401
from __future__ import annotations
from typing import TYPE_CHECKING
from ramda_py.types import *

if TYPE_CHECKING:
    from datetime import date, time, datetime
    from fitz import TextPage, Page, Document
    from argparse import ArgumentParser, _SubParsersAction

type Subparsers = _SubParsersAction[ArgumentParser]
type ValidationSubject = Literal["injuries", "treatments"]
type ValidatedResult = dict[ValidationVerdict, dict[str, tuple[float, list[str]]]]
type ValidationVerdict = Literal["verified", "unverified"]
type AnalysisResults = dict[ValidationSubject, list[str]]
type ValidationSummary = dict[ValidationSubject, dict[ValidationVerdict, int]]
