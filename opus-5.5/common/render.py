"""Render sheet: one PNG with six fixed views so a single image shows the
whole model. Views: iso front, iso back, top, front, cutaway, print plate."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pyvista as pv
from build123d import Keep, Location, split

from .export import plate_layout
from .geom import mesh_arrays, print_shape
from .model import Model

pv.OFF_SCREEN = True
EDGE_COLOR = "#2b2b2b"
BED_COLOR = "#9aa3ad"

# (label, view direction from target to camera, camera up, parallel projection)
VIEWS = [
    ("ISO FRONT-LEFT", (-1.0, -1.6, 1.1), (0, 0, 1)),
    ("ISO BACK-RIGHT", (1.2, 1.5, 1.1), (0, 0, 1)),
    ("TOP  (looking down -Z)", (0, 0, 1), (0, 1, 0)),
    ("FRONT  (looking +Y)", (0, -1, 0), (0, 0, 1)),
]


def to_pv(shape) -> pv.PolyData:
    v, f = mesh_arrays(shape)
    return pv.PolyData(v, np.hstack([np.full((len(f), 1), 3), f]).ravel())


def add_shape(pl: pv.Plotter, shape, color: str, opacity: float = 1.0):
    mesh = to_pv(shape).clean()   # merge per-face duplicate points so edges between faces are found
    pl.add_mesh(mesh, color=color, opacity=opacity, smooth_shading=True,
                split_sharp_edges=True, specular=0.2)
    edges = mesh.extract_feature_edges(feature_angle=35, boundary_edges=False,
                                       non_manifold_edges=False, manifold_edges=False)
    if edges.n_points:
        pl.add_mesh(edges, color=EDGE_COLOR, line_width=1.2)


def aim(pl: pv.Plotter, center, direction, up, zoom=1.0):
    d = np.array(direction, float)
    pl.camera.focal_point = center
    pl.camera.position = np.array(center) + d / np.linalg.norm(d) * 500
    pl.camera.up = up
    pl.enable_parallel_projection()
    pl.reset_camera()
    pl.camera.zoom(zoom)


def render_sheet(model: Model, path: Path):
    pl = pv.Plotter(shape=(2, 3), window_size=(2100, 1300), border_color="#cccccc")
    bb = model.parts[0].shape.bounding_box()
    for p in model.parts[1:]:
        bb = bb.add(p.shape.bounding_box())
    center = (bb.center().X, bb.center().Y, bb.center().Z)
    size = f"{bb.size.X:.1f} × {bb.size.Y:.1f} × {bb.size.Z:.1f} mm"

    for i, (label, direction, up) in enumerate(VIEWS):
        pl.subplot(i // 3, i % 3)
        for p in model.parts:
            add_shape(pl, p.shape, p.color, p.opacity)
        pl.add_text(label + ("   " + size if i == 0 else ""), font_size=10, color="black")
        pl.add_axes(line_width=3, labels_off=False)
        aim(pl, center, direction, up, 1.05)

    pl.subplot(1, 1)
    if model.section is not None:
        _cutaway(pl, model, center)
    else:
        pl.add_text("CUTAWAY  (no section plane set)", font_size=10, color="black")

    pl.subplot(1, 2)
    _plate(pl, model)

    pl.set_background("white")
    pl.screenshot(str(path))
    pl.close()


DETAIL_VIEWS = [("FRONT", (0, -1, 0.05)), ("3/4 FRONT-LEFT", (-1, -1, 0.3)), ("PROFILE (from +X)", (1, 0, 0.05))]


def render_detail(model: Model, path: Path):
    """Close-up of model.detail from the front, 3/4 and side: small features (faces, text,
    clips) are unreadable at whole-model zoom."""
    label, c, half = model.detail
    pl = pv.Plotter(shape=(1, 3), window_size=(1800, 650), border_color="#cccccc")
    for i, (name, d) in enumerate(DETAIL_VIEWS):
        pl.subplot(0, i)
        for p in model.parts:
            add_shape(pl, p.shape, p.color, p.opacity)
        pl.add_text(f"DETAIL: {label} — {name}", font_size=10, color="black")
        aim(pl, c, d, (0, 0, 1))
        pl.reset_camera(bounds=(c[0] - half, c[0] + half, c[1] - half, c[1] + half, c[2] - half, c[2] + half))
    pl.set_background("white")
    pl.screenshot(str(path))
    pl.close()


def _cutaway(pl, model: Model, center):
    plane = model.section
    cut_bb = None
    for p in model.parts:
        half = split(p.shape, bisect_by=plane, keep=Keep.BOTTOM)
        if not half or half.volume <= 0:
            continue
        add_shape(pl, half, p.color, p.opacity)
        cut = [f for f in half.faces()
               if abs(plane.to_local_coords(f.center()).Z) < 1e-3
               and abs(abs(f.normal_at().dot(plane.z_dir)) - 1) < 1e-6]
        for f in cut:
            pl.add_mesh(to_pv(f.moved(Location(plane.z_dir * 0.02))), color=_darken(p.color))
            fb = f.bounding_box()
            cut_bb = fb if cut_bb is None else cut_bb.add(fb)
    o, n = plane.origin, plane.z_dir
    pl.add_text(f"SECTION  looking along {_fmt_vec(-n)} at plane through {_fmt_vec(o)}  (cut faces darker)",
                font_size=10, color="black")
    pl.add_axes(line_width=3)
    up = (0, 0, 1) if abs(n.Z) < 0.9 else (0, 1, 0)
    c = cut_bb.center() if cut_bb else center
    aim(pl, (c.X, c.Y, c.Z), (n.X, n.Y, n.Z), up, 1.0)
    if cut_bb:
        pl.reset_camera(bounds=(cut_bb.min.X, cut_bb.max.X, cut_bb.min.Y, cut_bb.max.Y,
                                cut_bb.min.Z, cut_bb.max.Z))


def _darken(hex_color: str, k: float = 0.55) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return "#%02x%02x%02x" % (int(r * k), int(g * k), int(b * k))


def _fmt_vec(v) -> str:
    return "(" + ", ".join(f"{c + 0.0:.1f}" for c in (v.X, v.Y, v.Z)) + ")"


def _plate(pl, model: Model):
    shapes = [print_shape(p).moved(loc) for p, loc in zip(model.printed, plate_layout(model))]
    bb = shapes[0].bounding_box()
    for s in shapes[1:]:
        bb = bb.add(s.bounding_box())
    pad = 15
    bed = pv.Plane(center=(bb.center().X, bb.center().Y, -0.05), direction=(0, 0, 1),
                   i_size=bb.size.X + 2 * pad, j_size=bb.size.Y + 2 * pad)
    pl.add_mesh(bed, color=BED_COLOR, show_edges=False)
    for p, s in zip(model.printed, shapes):
        add_shape(pl, s, p.color)
    pl.add_text("PRINT PLATE  (as sliced, bed at z=0)", font_size=10, color="black")
    pl.add_axes(line_width=3)
    aim(pl, (bb.center().X, bb.center().Y, bb.center().Z), (-0.6, -1.4, 1.3), (0, 0, 1), 1.1)
