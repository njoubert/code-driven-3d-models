"""Small geometry helpers shared by checks, export and render."""

from __future__ import annotations

import numpy as np
from build123d import Location, Plane, Shape, Vector

from .model import Part

TESS_TOL = 0.02        # mm chordal deviation when meshing
TESS_ANGLE = 0.15      # radians


def print_shape(part: Part) -> Shape:
    """The part in print pose: rotated per `print_pose`, centred in XY, resting on z=0."""
    s = part.shape.moved(part.print_pose)
    bb = s.bounding_box()
    return s.moved(Location((-bb.center().X, -bb.center().Y, -bb.min.Z)))


def mesh_arrays(shape: Shape) -> tuple[np.ndarray, np.ndarray]:
    """Triangulate a shape -> (vertices Nx3, faces Mx3)."""
    verts, tris = shape.tessellate(TESS_TOL, TESS_ANGLE)
    v = np.array([(p.X, p.Y, p.Z) for p in verts], dtype=float)
    f = np.array(tris, dtype=np.int64).reshape(-1, 3)
    return v, f


def section(shape: Shape, plane: Plane):
    """Planar cross-section of `shape` -> list of Faces lying in `plane`."""
    result = shape.intersect(plane)
    return result.faces() if result else []


def as_xyz(v: Vector) -> tuple[float, float, float]:
    return (v.X, v.Y, v.Z)
