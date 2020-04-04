#!/usr/bin/python

from .micsync import Micsync as Micsync
from .version import _program_name
name = _program_name
__all__ = ["Micsync"]
# access after import example_pkg:
# micsync.Micsync()

