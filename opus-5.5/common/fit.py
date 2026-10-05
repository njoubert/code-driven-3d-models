"""Fit measurements for model checks: how far one shape can move before it hits another, and how
much of a face a bracket shadows. Everything is measured on the geometry, by boolean interference."""

from __future__ import annotations

from build123d import Box, Location, Vector


def union(shapes):
    u = shapes[0]
    for s in shapes[1:]:
        u = u + s
    return u


def overlap(a, b) -> float:
    return abs((a & b).volume) if a is not None else 0.0


def play(fixed, moving, axis: int, sign: int, hi: float = 3.0, tol: float = 0.005) -> float:
    """How far `moving` can slide along +/- `axis` before it touches `fixed` (bisection)."""
    def hits(d):
        v = [0.0, 0.0, 0.0]
        v[axis] = sign * d
        return overlap(fixed, moving.moved(Location(tuple(v)))) > 1e-4
    lo = 0.0
    if not hits(hi):
        return hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hits(mid) else (mid, hi)
    return lo


def lift_to_clear(fixed, moving, push: float = 3.0, tol: float = 0.05, hi: float = 10.0) -> float:
    """How far `moving` must be lifted before it can be pushed `push` mm along -y (forward; negative: back)
    without a collision; `hi` if not even then."""
    lo = 0.0
    hits = lambda z: overlap(fixed, moving.moved(Location((0, -push, z)))) > 1e-4
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if hits(mid) else (lo, mid)
    return hi


def face_coverage(device, brackets, axis: int, side: int, inset: float = 0.0, reach: float = 8.0,
                  insets: dict | None = None) -> float:
    """Fraction of a device face shadowed by bracket material within `reach` mm of it,
    ignoring an `inset` border (or per-axis `insets`, {axis index: mm}). Projected area
    from a slab in front of the face."""
    b = device.bounding_box()
    lo, hi = [b.min.X, b.min.Y, b.min.Z], [b.max.X, b.max.Y, b.max.Z]
    a, o = axis, [i for i in range(3) if i != axis]
    size, centre = [0.0] * 3, [0.0] * 3
    for i in o:
        size[i] = hi[i] - lo[i] - 2 * (insets.get(i, inset) if insets else inset)
        centre[i] = (hi[i] + lo[i]) / 2
    size[a] = reach
    centre[a] = (hi[a] + reach / 2 + 0.01) if side > 0 else (lo[a] - reach / 2 - 0.01)
    slab = Box(*size).moved(Location(tuple(centre)))
    hit = slab & brackets
    if not hit or abs(hit.volume) < 1e-6:
        return 0.0
    n = [0.0, 0.0, 0.0]
    n[a] = 1.0
    proj = sum(f.area * abs(f.normal_at().dot(Vector(*n))) for f in hit.faces()) / 2
    return min(proj / (size[o[0]] * size[o[1]]), 1.0)
