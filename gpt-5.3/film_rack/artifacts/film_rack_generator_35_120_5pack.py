import trimesh
import numpy as np
from shapely.geometry import Polygon
import sys

# ============================================================
# Film Box Rack Generator
# ============================================================
#
# Generates a 3D-printable rack for storing film boxes, single
# rolls, or 5-packs. Output is an STL file ready for slicing.
#
# SUPPORTED FILM TYPES
# --------------------
#   "35mm"       — 35mm film boxes (40mm wide cubbies)
#   "120"        — Single 120 medium format rolls (31mm cubbies)
#   "120-5pack"  — 120 five-pack boxes (138mm wide shelves)
#
# TERMINOLOGY
# -----------
# Rack      — The complete assembled unit: a grid of shelves
#             sharing walls, with a solid back panel.
#
# Shelf     — A single cubby that holds one item. Each shelf
#             is an open-front rectangular cell.
#
# Trapezoid — The tapered arm extending forward from the front
#             edge of each shelf floor. Narrows from a base
#             width down to a narrow tip (TRAP_TIP). Guides the
#             item and provides a platform for the lip.
#
# Lip       — A small vertical wall at the tip of the trapezoid
#             that prevents the item from sliding out on its own.
#
# Scoop     — A semicircular cutout on each vertical wall,
#             visible from the side profile. Saves material and
#             print time.
#
# For 5-pack shelves, there are TWO trapezoids per shelf, spaced
# evenly across the shelf width (with equal gap-trap-gap-trap-gap
# spacing). Their base width matches the single 120 cubby's
# trapezoid base for visual consistency.
#
# PRINTING TIPS
# -------------
# - Print on its back (back wall flat on bed). Shelves become
#   vertical walls needing no support. The small lip overhangs
#   bridge fine without supports.
# - Use 3+ perimeters for wall strength.
# - PETG recommended for durability; PLA works fine too.
#
# DEPENDENCIES
# ------------
# pip install trimesh manifold3d shapely numpy
#
# ============================================================
#
# USER SETTINGS — change these three values:
#

FILM_TYPE = "35mm"    # "35mm", "120", or "120-5pack"
COLS      = 4
ROWS      = 5

# ============================================================
# Film-type-specific parameters
# ============================================================
#
# Each profile defines the cubby geometry and trapezoid setup.
# TRAP_COUNT is how many trapezoids each shelf gets.
# TRAP_BASE_WIDTH of None means the trapezoid base spans the
# full slot width.

FILM_PROFILES = {
    "35mm": {
        "RACK_DEPTH":      43.2,
        "LIP_HEIGHT":      4.0,
        "OVERHANG":        21.3,
        "SLOT_WIDTH":      40.0,
        "SLOT_HEIGHT":     42.0,
        "SCOOP_RATIO":     0.60,
        "TRAP_BASE_WIDTH": None,
        "TRAP_COUNT":      1,
    },
    "120": {
        "RACK_DEPTH":      50.0,
        "LIP_HEIGHT":      3.5,
        "OVERHANG":        32.6,
        "SLOT_WIDTH":      31.0,
        "SLOT_HEIGHT":     33.0,
        "SCOOP_RATIO":     0.80,
        "TRAP_BASE_WIDTH": None,
        "TRAP_COUNT":      1,
    },
    "120-5pack": {
        "RACK_DEPTH":      50.0,
        "LIP_HEIGHT":      3.5,
        "OVERHANG":        32.6,
        "SLOT_WIDTH":      138.0,
        "SLOT_HEIGHT":     33.0,
        "SCOOP_RATIO":     0.80,
        "TRAP_BASE_WIDTH": 31.0,   # match single 120 cubby trap base
        "TRAP_COUNT":      2,
    },
}

if FILM_TYPE not in FILM_PROFILES:
    valid = ", ".join(f"'{k}'" for k in FILM_PROFILES)
    print(f"Unknown film type '{FILM_TYPE}'. Choose from: {valid}.")
    sys.exit(1)

profile = FILM_PROFILES[FILM_TYPE]
RACK_DEPTH      = profile["RACK_DEPTH"]
LIP_HEIGHT      = profile["LIP_HEIGHT"]
OVERHANG        = profile["OVERHANG"]
SLOT_WIDTH      = profile["SLOT_WIDTH"]
SLOT_HEIGHT     = profile["SLOT_HEIGHT"]
SCOOP_RATIO     = profile["SCOOP_RATIO"]
TRAP_BASE_WIDTH = profile["TRAP_BASE_WIDTH"] or SLOT_WIDTH
TRAP_COUNT      = profile["TRAP_COUNT"]

# ============================================================
# Shared parameters (same for all film types)
# ============================================================
WALL           = 1.3
SHELF_WALL     = 1.6
BACK_WALL      = 2.0
TRAP_TIP       = 5.0
SCOOP_SEGMENTS = 64

# ============================================================
# Derived dimensions
# ============================================================
TOTAL_WIDTH  = COLS * SLOT_WIDTH + (COLS + 1) * WALL
TOTAL_HEIGHT = ROWS * SLOT_HEIGHT + (ROWS + 1) * SHELF_WALL
TOTAL_DEPTH  = RACK_DEPTH + BACK_WALL

print(f"Film type: {FILM_TYPE}")
print(f"Grid: {COLS} x {ROWS} = {COLS * ROWS} shelves, "
      f"{TRAP_COUNT} trapezoid{'s' if TRAP_COUNT != 1 else ''} each")
print(f"Rack: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"With overhang: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH + OVERHANG:.1f} x {TOTAL_HEIGHT:.1f} mm")


def trap_centers_for_shelf(shelf_x_left, shelf_width):
    """
    X positions of trapezoid centers within a shelf.
    
    TRAP_COUNT trapezoids with equal gaps between them and at
    both ends (so gap-trap-gap-trap-gap... has uniform gaps).
    Works for any count: 1, 2, 3, etc.
    """
    n = TRAP_COUNT
    gap = (shelf_width - n * TRAP_BASE_WIDTH) / (n + 1)
    return [
        shelf_x_left + (i + 1) * gap + (i + 0.5) * TRAP_BASE_WIDTH
        for i in range(n)
    ]


# ============================================================
# Build outer shell with all cavities
# ============================================================
outer = trimesh.creation.box(extents=[TOTAL_WIDTH, TOTAL_DEPTH, TOTAL_HEIGHT])
outer.apply_translation([TOTAL_WIDTH/2, TOTAL_DEPTH/2, TOTAL_HEIGHT/2])
result = outer

for row in range(ROWS):
    for col in range(COLS):
        x_center = col * (SLOT_WIDTH + WALL) + WALL + SLOT_WIDTH/2
        z_center = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
        cavity = trimesh.creation.box(extents=[SLOT_WIDTH, RACK_DEPTH + WALL + 1, SLOT_HEIGHT])
        cavity.apply_translation([x_center, (RACK_DEPTH - 1)/2, z_center])
        result = trimesh.boolean.difference([result, cavity], engine='manifold')

# ============================================================
# Semicircular scoops on all vertical walls
# ============================================================
scoop_r = SCOOP_RATIO * SLOT_HEIGHT / 2.0

cyl_template = trimesh.creation.cylinder(radius=scoop_r, height=WALL + 0.5, sections=SCOOP_SEGMENTS)
rot = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
cyl_template.apply_transform(rot)
front_cut_template = trimesh.creation.box(extents=[WALL + 2, scoop_r * 2 + 10, scoop_r * 2 + 10])

for row in range(ROWS):
    scoop_cz = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
    
    wall_positions = [WALL/2, TOTAL_WIDTH - WALL/2]
    for col in range(1, COLS):
        wall_positions.append(col * (SLOT_WIDTH + WALL) + WALL/2)
    
    for wall_x in wall_positions:
        cyl = cyl_template.copy()
        cyl.apply_translation([wall_x, 0, scoop_cz])
        front_cut = front_cut_template.copy()
        front_cut.apply_translation([wall_x, -(scoop_r + 5) - 0.1, scoop_cz])
        half_cyl = trimesh.boolean.difference([cyl, front_cut], engine='manifold')
        result = trimesh.boolean.difference([result, half_cyl], engine='manifold')

print("Shell with cutouts done")

# ============================================================
# Trapezoid arms + lips for each shelf
# ============================================================
extras = []
for row in range(ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col in range(COLS):
        shelf_x_left = col * (SLOT_WIDTH + WALL) + WALL
        
        for cx in trap_centers_for_shelf(shelf_x_left, SLOT_WIDTH):
            base_left  = cx - TRAP_BASE_WIDTH / 2.0
            base_right = cx + TRAP_BASE_WIDTH / 2.0
            tip_left   = cx - TRAP_TIP / 2.0
            tip_right  = cx + TRAP_TIP / 2.0
            
            trap_poly = Polygon([
                (base_left, 0),
                (base_right, 0),
                (tip_right, -OVERHANG),
                (tip_left, -OVERHANG),
            ])
            trap_mesh = trimesh.creation.extrude_polygon(trap_poly, height=SHELF_WALL)
            trap_mesh.apply_translation([0, 0, shelf_z])
            extras.append(trap_mesh)
            
            lip = trimesh.creation.box(extents=[TRAP_TIP, SHELF_WALL, LIP_HEIGHT])
            lip.apply_translation([cx, -OVERHANG + SHELF_WALL/2, shelf_z + SHELF_WALL + LIP_HEIGHT/2])
            extras.append(lip)

print(f"Adding {len(extras)} trapezoids and lips")
result = trimesh.boolean.union([result] + extras, engine='manifold')

# ============================================================
# Save
# ============================================================
out_path = f"film_rack_{FILM_TYPE}_{COLS}x{ROWS}.stl"
result.export(out_path)
print(f"Saved to {out_path}")
print(f"Vertices: {len(result.vertices)}, Faces: {len(result.faces)}")
bounds = result.bounds
print(f"Size: {bounds[1] - bounds[0]}")
