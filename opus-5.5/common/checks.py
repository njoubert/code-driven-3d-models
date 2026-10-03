"""Checks: generic printability checks for every part, plus a Report that
model-specific checks write into. Failures make the run exit non-zero."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from .geom import mesh_arrays, print_shape
from .model import Model

# Bambu Lab P2S build volume (same as X1/P1 series).
BED = (256.0, 256.0, 256.0)
OVERHANG_DEG = 45.0          # faces steeper than this from vertical need support
OVERHANG_WARN_MM2 = 20.0     # total unsupported area worth mentioning


@dataclass
class Result:
    level: str    # "PASS" | "WARN" | "FAIL"
    name: str
    detail: str


class Report:
    def __init__(self):
        self.results: list[Result] = []

    def add(self, level: str, name: str, detail: str = ""):
        self.results.append(Result(level, name, detail))

    def check(self, name: str, ok: bool, detail: str = "", warn_only: bool = False):
        self.add("PASS" if ok else ("WARN" if warn_only else "FAIL"), name, detail)

    def dim(self, name: str, measured: float, expected: float, tol: float = 0.05):
        """Assert a measured dimension equals the design value within `tol` mm."""
        self.check(name, abs(measured - expected) <= tol,
                   f"measured {measured:.3f}, expected {expected:.3f} ±{tol}")

    def at_least(self, name: str, measured: float, minimum: float, warn_only: bool = False):
        self.check(name, measured >= minimum - 1e-6,
                   f"measured {measured:.3f}, minimum {minimum:.3f}", warn_only)

    @property
    def failed(self) -> bool:
        return any(r.level == "FAIL" for r in self.results)

    def print(self):
        width = max(len(r.name) for r in self.results)
        for r in self.results:
            print(f"  {r.level:4}  {r.name:<{width}}  {r.detail}")
        n = {lvl: sum(r.level == lvl for r in self.results) for lvl in ("PASS", "WARN", "FAIL")}
        print(f"  -> {n['PASS']} pass, {n['WARN']} warn, {n['FAIL']} fail")


def generic_checks(model: Model, report: Report):
    for part in model.printed:
        s = part.shape
        report.check(f"{part.name}: valid B-rep", s.is_valid)
        solids = len(s.solids())
        report.check(f"{part.name}: single solid", solids == 1, f"{solids} solid(s)")
        report.check(f"{part.name}: positive volume", s.volume > 0, f"{s.volume / 1000:.2f} cm³")

        ps = print_shape(part)
        size = ps.bounding_box().size
        fits = all(d <= b for d, b in zip((size.X, size.Y, size.Z), BED))
        report.check(f"{part.name}: fits bed", fits,
                     f"print size {size.X:.1f} × {size.Y:.1f} × {size.Z:.1f} mm")

        area, zmax = overhang_area(ps)
        report.check(f"{part.name}: overhangs", area < OVERHANG_WARN_MM2,
                     f"{area:.1f} mm² steeper than {OVERHANG_DEG:.0f}° off the bed"
                     + (f" (highest at z={zmax:.1f})" if area else ""), warn_only=True)


def overhang_area(shape) -> tuple[float, float]:
    """Area of downward-facing triangles steeper than OVERHANG_DEG that aren't on the bed."""
    v, f = mesh_arrays(shape)
    tri = v[f]
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    area = np.linalg.norm(n, axis=1) / 2
    nz = n[:, 2] / np.maximum(np.linalg.norm(n, axis=1), 1e-12)
    zmin = tri[:, :, 2].min(axis=1)
    bad = (nz < -np.sin(np.radians(90 - OVERHANG_DEG))) & (zmin > 0.05)
    return float(area[bad].sum()), float(tri[bad][:, :, 2].max()) if bad.any() else 0.0


def run_checks(model: Model) -> Report:
    report = Report()
    generic_checks(model, report)
    if model.checks:
        model.checks(report, {p.name: p for p in model.parts})
    return report
