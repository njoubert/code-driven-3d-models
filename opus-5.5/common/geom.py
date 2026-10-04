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


SEAM_ANGLES = (0, 90, 180, 270, 45, 135, 225, 315)


def fuse_robust(named_makers, angles=SEAM_ANGLES):
    """Fuse pieces one at a time, verifying each step.

    named_makers: [(name, make)], where make(angle) builds the piece with its seam (the
    line where a sphere/cylinder surface closes on itself) rotated by `angle` degrees,
    without changing its shape. OpenCascade booleans can silently drop a piece or produce
    an invalid solid when a seam or pole lands where pieces meet; on failure the piece is
    retried with the seam elsewhere.
    -> (union, [(name, piece used)], [names that failed at every angle])
    """
    acc, used, failed = None, [], []
    for name, make in named_makers:
        for angle in angles:
            piece = make(angle)
            if acc is None:
                acc = piece
                break
            cand = acc.fuse(piece).clean()
            # abs(): an intersection can come back inside-out, with negative volume
            if cand.is_valid and len(cand.solids()) == 1 and abs((cand & piece).volume) >= piece.volume * 0.99:
                acc = cand
                break
        else:
            failed.append(name)
            continue
        used.append((name, piece))
    return acc, used, failed


def as_xyz(v: Vector) -> tuple[float, float, float]:
    return (v.X, v.Y, v.Z)
