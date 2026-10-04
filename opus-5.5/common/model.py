"""Data types a model's `build()` returns to the harness.

A model is a set of named parts in their *use* pose (assembled, how the
object sits on your desk), plus the information the harness needs to
check, export, render and draw it.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable

from build123d import Location, Plane
from build123d import Part as Solid


@dataclass
class Part:
    name: str
    shape: Solid                       # in use pose, millimetres
    color: str = "#d8c9a8"
    print_pose: Location = field(default_factory=Location)  # use pose -> print pose (harness drops it onto z=0)
    explode: tuple[float, float, float] = (0, 0, 0)          # offset used by the 3D viewer's explode slider
    reference: bool = False            # True = not printed (e.g. the pill); rendered only, skipped by export/print checks
    opacity: float = 1.0               # < 1 renders see-through (e.g. a reference desk you look through)


@dataclass
class Dim:
    """A linear dimension on a drawing view.

    p1, p2 are 3D model points; the dimension measures their separation
    along the paper's horizontal ("h") or vertical ("v") axis in `view`.
    `offset` is paper mm outside the view's outline: for "h", + = above the
    view, − = below; for "v", + = right of it, − = left. Stack dims at
    8, 16, 24 … Extension lines run from p1/p2 to the dimension line.
    """
    view: str                          # "front" | "top" | "right"
    p1: tuple[float, float, float]
    p2: tuple[float, float, float]
    axis: str                          # "h" | "v"
    offset: float
    text: str | None = None            # override the measured value, e.g. "7× 11"


@dataclass
class Note:
    """A leader note: arrow at 3D point `at` in `view`, text placed outside the
    view on `side` ("above" | "below" | "left" | "right"), beyond any dimensions
    there, shifted `along` paper mm (right for above/below, up for left/right)."""
    view: str
    at: tuple[float, float, float]
    text: str
    side: str = "above"
    along: float = 0.0


@dataclass
class Sheet:
    """One technical drawing sheet for one part."""
    part: str
    dims: list[Dim] = field(default_factory=list)
    notes: list[Note] = field(default_factory=list)
    material: str = "PLA"
    show_hidden: bool = True


@dataclass
class Model:
    name: str
    title: str
    parts: list[Part]
    sheets: list[Sheet] = field(default_factory=list)
    checks: Callable | None = None     # checks(report, parts_by_name) -> None
    section: Plane | None = None       # cutaway plane for the render sheet; keeps the side opposite the normal
    slicer: dict = field(default_factory=dict)  # Bambu Studio setting overrides, e.g. {"enable_support": "1"}
    detail: tuple | None = None        # close-up for small features: (label, centre xyz, half-size mm)

    def part(self, name: str) -> Part:
        return next(p for p in self.parts if p.name == name)

    @property
    def printed(self) -> list[Part]:
        return [p for p in self.parts if not p.reference]
