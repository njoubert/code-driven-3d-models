"""Technical drawing sheets: front / top / right orthographic views in
third-angle projection, an isometric view, dimensions, leader notes and a
title block on one A4/A3 page. Writes PDF (vector, printable) and PNG.

Edges come from OpenCascade's hidden-line removal (`project_to_viewport`),
so visible and hidden lines are exact, not traced from a mesh render.
"""

from __future__ import annotations

import datetime
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from build123d import GeomType, PositionMode
from matplotlib.patches import Circle, Polygon, Rectangle

from .model import Dim, Model, Note, Sheet

PAPERS = [("A4", 297.0, 210.0), ("A3", 420.0, 297.0)]
SCALES = [10, 5, 4, 2, 1, 0.5, 0.25, 0.2, 0.1]
MARGIN = 10.0          # paper edge -> border
PAD = 24.0             # border -> views, and space for dimensions around views
GAP = 28.0             # between views
TITLE_W, TITLE_H = 140.0, 34.0
MIN_ISO = (55.0, 45.0)

PT = 72 / 25.4         # points per mm
LW_VISIBLE, LW_HIDDEN, LW_THIN, LW_BORDER = 0.5, 0.25, 0.18, 0.7   # mm
TEXT_DIM, TEXT_LABEL = 3.2, 3.0                                    # mm cap height-ish
INK = "#111111"

# view -> (direction to viewer, up, (u axis index, v axis index) of model XYZ)
VIEWS = {
    "front": ((0, -1, 0), (0, 0, 1), (0, 2)),
    "top":   ((0, 0, 1), (0, 1, 0), (0, 1)),
    "right": ((1, 0, 0), (0, 0, 1), (1, 2)),
}
ISO_DIR = ((1, -1, 1), (0, 0, 1))


@dataclass
class Placed:
    """A view placed on paper: paper = origin + (model_uv - uv_min) * scale."""
    origin: np.ndarray
    uv_min: np.ndarray
    scale: float
    axes: tuple[int, int]
    size: np.ndarray       # paper mm

    def __call__(self, p3) -> np.ndarray:
        uv = np.array([p3[self.axes[0]], p3[self.axes[1]]], float)
        return self.origin + (uv - self.uv_min) * self.scale


def draw_sheets(model: Model, out: Path) -> list[Path]:
    written = []
    for i, sheet in enumerate(model.sheets):
        part = model.part(sheet.part)
        if not sheet.dims:
            sheet.dims = overall_dims(part.shape)
        stem = out / f"drawing_{sheet.part}"
        _draw(model, sheet, part.shape, stem, i + 1, len(model.sheets))
        written += [stem.with_suffix(".pdf"), stem.with_suffix(".png")]
    return written


def overall_dims(shape) -> list[Dim]:
    """Default dimensions: overall width and height on the front view, depth on the right."""
    b = shape.bounding_box()
    lo, hi = (b.min.X, b.min.Y, b.min.Z), (b.max.X, b.max.Y, b.max.Z)
    return [
        Dim("front", (lo[0], lo[1], lo[2]), (hi[0], lo[1], lo[2]), "h", -8),
        Dim("front", (lo[0], lo[1], lo[2]), (lo[0], lo[1], hi[2]), "v", -8),
        Dim("right", (hi[0], lo[1], lo[2]), (hi[0], hi[1], lo[2]), "h", -8),
    ]


# ---------------------------------------------------------------- layout

def _extent(bb, axes):
    lo = np.array([bb.min.X, bb.min.Y, bb.min.Z])
    hi = np.array([bb.max.X, bb.max.Y, bb.max.Z])
    return lo[list(axes)], (hi - lo)[list(axes)]


def _layout(shape):
    """Pick the largest standard scale (then smallest paper) that fits."""
    bb = shape.bounding_box()
    X, Y, Z = bb.size.X, bb.size.Y, bb.size.Z
    for s in SCALES:
        for paper, W, H in PAPERS:
            left, bottom = MARGIN + PAD, MARGIN + PAD
            right, top = W - MARGIN - PAD, H - MARGIN - PAD
            block_w, block_h = (X + Y) * s + GAP, (Z + Y) * s + GAP
            # lift the views above the title block if the right view would hit it
            if left + block_w > W - MARGIN - TITLE_W - 4:
                bottom = max(bottom, MARGIN + TITLE_H + PAD * 0.6)
            if left + block_w > right or bottom + block_h > top:
                continue
            front = np.array([left, bottom])
            top_o = front + [0, Z * s + GAP]
            right_o = front + [X * s + GAP, 0]
            # isometric goes in the largest free rectangle: above the right view,
            # or to the right of the whole block (above the title block)
            cands = [
                (right_o[0], bottom + Z * s + GAP * 0.7, right, top),
                (left + block_w + GAP * 0.7, MARGIN + TITLE_H + 8, right, top),
            ]
            cands = [c for c in cands if c[2] - c[0] >= MIN_ISO[0] and c[3] - c[1] >= MIN_ISO[1]]
            if not cands:
                continue
            iso = max(cands, key=lambda c: (c[2] - c[0]) * (c[3] - c[1]))
            return paper, W, H, s, {"front": front, "top": top_o, "right": right_o}, iso
    raise ValueError("part too large for an A3 sheet at 1:10")


# ---------------------------------------------------------------- drawing

def _draw(model: Model, sheet: Sheet, shape, stem: Path, n: int, total: int):
    paper, W, H, s, origins, iso_box = _layout(shape)
    fig = plt.figure(figsize=(W / 25.4, H / 25.4))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W), ax.set_ylim(0, H), ax.set_aspect("equal"), ax.axis("off")

    ax.add_patch(Rectangle((MARGIN, MARGIN), W - 2 * MARGIN, H - 2 * MARGIN,
                           fill=False, lw=LW_BORDER * PT, ec=INK))

    bb = shape.bounding_box()
    placed = {}
    for name, (direction, up, axes) in VIEWS.items():
        uv_min, uv_size = _extent(bb, axes)
        placed[name] = Placed(origins[name], uv_min, s, axes, uv_size * s)
        visible, hidden = shape.project_to_viewport(direction, up, (0, 0, 0))
        # projected edges live in viewport coords that equal the model (u, v) axes
        to_paper = lambda q: origins[name] + (np.asarray(q) - uv_min) * s
        _edges(ax, visible, to_paper, LW_VISIBLE, "-")
        if sheet.show_hidden:
            _edges(ax, hidden, to_paper, LW_HIDDEN, (0, (3, 1.5)))

    _iso(ax, shape, iso_box)
    for d in sheet.dims:
        _dim(ax, placed[d.view], d)
    for name, view in placed.items():   # view label under the view, below its dimensions
        y = view.origin[1] - _used(sheet, name, "below") - 3
        if y - TEXT_LABEL < MARGIN + 2:     # no room below (dims reach the border): label above instead
            y, va = view.origin[1] + view.size[1] + _used(sheet, name, "above") + 2, "bottom"
        else:
            va = "top"
        ax.text(view.origin[0], y, name.upper(), fontsize=TEXT_LABEL * PT, color=INK,
                ha="left", va=va, weight="bold")
    for note in sheet.notes:
        _note(ax, placed[note.view], note, sheet)
    _title_block(ax, W, model, sheet, s, paper, n, total)

    fig.savefig(stem.with_suffix(".pdf"), metadata={"CreationDate": None})  # stable bytes for git
    fig.savefig(stem.with_suffix(".png"), dpi=170, facecolor="white")
    plt.close(fig)


def _polyline(edge) -> np.ndarray:
    if edge.geom_type == GeomType.LINE:
        ts = [0.0, 1.0]
    else:
        ts = np.linspace(0, 1, int(np.clip(edge.length / 0.25, 8, 400)))
    # sample by curve parameter, not arc length: arc-length lookup fails on some freeform outlines
    pts = (edge.position_at(t, position_mode=PositionMode.PARAMETER) for t in ts)
    return np.array([[p.X, p.Y] for p in pts])


def _edges(ax, edges, to_paper, lw, style):
    failed = 0
    for e in edges:
        try:
            pts = to_paper(_polyline(e))
        except Exception:
            failed += 1
            continue
        ax.plot(pts[:, 0], pts[:, 1], color=INK, lw=lw * PT, ls=style,
                solid_capstyle="round", dash_capstyle="butt")
    if failed:
        print(f"  drawing: skipped {failed} edge(s) that could not be sampled")


def _iso(ax, shape, box):
    x0, y0, x1, y1 = box
    visible, _ = shape.project_to_viewport(*ISO_DIR, (0, 0, 0))
    lines = [_polyline(e) for e in visible]
    allpts = np.vstack(lines)
    lo, hi = allpts.min(axis=0), allpts.max(axis=0)
    k = min((x1 - x0) / (hi - lo)[0], (y1 - y0 - 8) / (hi - lo)[1]) * 0.9
    centre = np.array([(x0 + x1) / 2, (y0 + y1) / 2 + 4])
    for pts in lines:
        q = centre + (pts - (lo + hi) / 2) * k
        ax.plot(q[:, 0], q[:, 1], color=INK, lw=LW_VISIBLE * PT * 0.8, solid_capstyle="round")
    ax.text(centre[0], y0, "ISOMETRIC  (not to scale)", fontsize=TEXT_LABEL * PT,
            ha="center", va="bottom", color=INK)


def _fmt(v: float) -> str:
    return f"{v:.2f}".rstrip("0").rstrip(".")


def _dim(ax, view: Placed, d: Dim):
    a, b = view(d.p1), view(d.p2)
    i = 0 if d.axis == "h" else 1      # measured paper axis
    j = 1 - i                          # offset direction
    lo, hi = view.origin[j], view.origin[j] + view.size[j]
    line = hi + d.offset if d.offset > 0 else lo + d.offset
    value = abs(b[i] - a[i]) / view.scale
    text = d.text or _fmt(value)
    kw = dict(color=INK, lw=LW_THIN * PT)

    for p in (a, b):                   # extension lines: 1 mm gap from part, 2 mm past dim line
        sign = np.sign(line - p[j]) or 1
        start, end = p[j] + sign * 1.0, line + sign * 2.0
        if abs(line - p[j]) > 1.5:
            xs, ys = ([p[0], p[0]], [start, end]) if i == 0 else ([start, end], [p[1], p[1]])
            ax.plot(xs, ys, **kw)

    p1, p2 = a.copy(), b.copy()
    p1[j] = p2[j] = line
    ax.annotate("", xy=p1, xytext=p2,
                arrowprops=dict(arrowstyle="<|-|>", color=INK, lw=LW_THIN * PT,
                                mutation_scale=7, shrinkA=0, shrinkB=0))
    mid = (p1 + p2) / 2
    span = abs(p2[i] - p1[i])
    fits = span > len(text) * TEXT_DIM * 0.62 + 6
    if i == 0:
        pos = (mid[0], line + 0.8) if fits else (max(p1[0], p2[0]) + 2, line + 0.8)
        ax.text(*pos, text, fontsize=TEXT_DIM * PT, ha="center" if fits else "left",
                va="bottom", color=INK)
    else:
        pos = (line - 0.8, mid[1]) if fits else (line - 0.8, max(p1[1], p2[1]) + 2)
        ax.text(*pos, text, fontsize=TEXT_DIM * PT, rotation=90, ha="right",
                va="center" if fits else "bottom", color=INK)


def _side(d: Dim) -> str:
    if d.axis == "h":
        return "above" if d.offset > 0 else "below"
    return "right" if d.offset > 0 else "left"


def _used(sheet: Sheet, view: str, side: str) -> float:
    """Paper mm beyond the view outline taken by dimensions (and the label, below)."""
    offs = [abs(d.offset) for d in sheet.dims if d.view == view and _side(d) == side]
    used = max(offs) + TEXT_DIM + 2 if offs else 2
    return used + (TEXT_LABEL + 4 if side == "below" else 0)


def _note(ax, view: Placed, note: Note, sheet: Sheet):
    p = view(note.at)
    gap = _used(sheet, note.view, note.side) + 4
    x0, y0 = view.origin
    x1, y1 = view.origin + view.size
    pos, ha, va = {
        "above": ((p[0] + note.along, y1 + gap), "left", "bottom"),
        "below": ((p[0] + note.along, y0 - gap), "left", "top"),
        "right": ((x1 + gap, p[1] + note.along), "left", "center"),
        "left":  ((x0 - gap, p[1] + note.along), "right", "center"),
    }[note.side]
    ax.annotate(note.text, xy=p, xytext=pos, fontsize=TEXT_DIM * PT, color=INK, ha=ha, va=va,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=LW_THIN * PT,
                                mutation_scale=6, shrinkA=1, shrinkB=0))


def _title_block(ax, W, model: Model, sheet: Sheet, s: float, paper: str, n: int, total: int):
    x0, y0 = W - MARGIN - TITLE_W, MARGIN
    kw = dict(fill=False, lw=LW_BORDER * PT * 0.7, ec=INK)
    ax.add_patch(Rectangle((x0, y0), TITLE_W, TITLE_H, **kw))
    ax.plot([x0, x0 + TITLE_W], [y0 + 14, y0 + 14], color=INK, lw=LW_THIN * PT)
    cols = [0, 34, 62, 98, TITLE_W]
    for c in cols[1:-1]:
        ax.plot([x0 + c, x0 + c], [y0, y0 + 14], color=INK, lw=LW_THIN * PT)
    ax.plot([x0 + 98, x0 + 98], [y0 + 14, y0 + TITLE_H], color=INK, lw=LW_THIN * PT)

    def cell(cx, cy, label, value, size=3.0):
        ax.text(x0 + cx + 1.5, y0 + cy + 11.5, label, fontsize=1.8 * PT, color="#555", va="top")
        ax.text(x0 + cx + 1.5, y0 + cy + 2.5, value, fontsize=size * PT, color=INK, va="bottom")

    title_size = min(5.0, 5.0 * 30 / max(len(model.title), 1))   # shrink long titles to fit beside SCALE
    ax.text(x0 + 3, y0 + TITLE_H - 4, model.title, fontsize=title_size * PT, color=INK, va="top", weight="bold")
    ax.text(x0 + 3, y0 + 16.5, f"part: {sheet.part}", fontsize=3.2 * PT, color=INK, va="bottom")
    scale = f"{int(s)}:1" if s >= 1 else f"1:{int(round(1 / s))}"
    ax.text(x0 + 99.5, y0 + TITLE_H - 2.5, "SCALE", fontsize=1.8 * PT, color="#555", va="top")
    ax.text(x0 + 119, y0 + 17, scale, fontsize=6 * PT, color=INK, ha="center", va="bottom", weight="bold")
    cell(cols[0], 0, "MATERIAL", sheet.material)
    cell(cols[1], 0, "UNITS", "mm")
    cell(cols[2], 0, "DATE", datetime.date.today().isoformat())
    cell(cols[3], 0, f"{paper}  ·  SHEET {n}/{total}", "")
    _third_angle_symbol(ax, x0 + cols[3] + 9, y0 + 1.2)


def _third_angle_symbol(ax, x, y):
    """ASME third-angle symbol: frustum side view, then end view seen from its narrow end."""
    kw = dict(fill=False, ec=INK, lw=LW_THIN * PT * 1.3)
    ax.add_patch(Polygon([(x, y), (x + 10, y + 1.5), (x + 10, y + 5.5), (x, y + 7)], closed=True, **kw))
    ax.add_patch(Circle((x + 18, y + 3.5), 3.5, **kw))
    ax.add_patch(Circle((x + 18, y + 3.5), 2.0, **kw))
    ax.plot([x - 1.5, x + 23], [y + 3.5, y + 3.5], color=INK, lw=LW_THIN * PT * 0.8, ls=(0, (6, 1.5, 1, 1.5)))
