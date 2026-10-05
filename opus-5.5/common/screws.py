"""The owner's standard screw: #6 × 5/8" flat-head construction screws, driven up into the desk.
A countersunk hole for it, and a reference screw to check that its head seats."""

from __future__ import annotations

import math

from build123d import Align, Cone, Cylinder, Location

C, MIN = Align.CENTER, Align.MIN

SCREW_SIZE, SCREW_L, SCREW_HEAD = 3.5, 15.9, 6.9   # shank, length (5/8"), head diameter (~6.9 mm)
SCREW_D = 4.0                  # clearance hole (printed holes come out a little small)
CSK_D, CSK_ANGLE = 7.4, 82.0   # countersink: a little over the head, so it seats flush; imperial 82°


def countersunk(x, y, z_bottom, length):
    """Screw hole up into the desk, countersunk from the underside at z_bottom."""
    t = math.tan(math.radians(CSK_ANGLE / 2))
    h = (CSK_D - SCREW_D) / 2 / t
    return (Cylinder(SCREW_D / 2, length + 2, align=(C, C, MIN)).moved(Location((x, y, z_bottom - 1)))
            + Cone(CSK_D / 2 + 0.1 * t, SCREW_D / 2, h + 0.1, align=(C, C, MIN)).moved(Location((x, y, z_bottom - 0.1))))


def screw(x, y, z_bottom):
    """Reference #6 flat-head screw, head flush with the flange's underside at z_bottom, going up."""
    t = math.tan(math.radians(CSK_ANGLE / 2))
    h = (SCREW_HEAD - SCREW_SIZE) / 2 / t
    head = Cone(SCREW_HEAD / 2, SCREW_SIZE / 2, h, align=(C, C, MIN))
    return (head + Cylinder(SCREW_SIZE / 2, SCREW_L - h, align=(C, C, MIN)).moved(Location((0, 0, h)))).moved(
        Location((x, y, z_bottom)))
