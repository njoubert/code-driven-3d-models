import trimesh
import numpy as np
from shapely.geometry import Polygon
import sys

# ============================================================
# Film Box Rack Generator
# ============================================================
#
# Generates a 3D-printable rack for storing 35mm or 120 medium
# format film boxes. Output is an STL file ready for slicing.
#
# TERMINOLOGY
# -----------
# Rack     — The complete assembled unit: a grid of shelves
#             sharing walls, with a solid back panel.
#
# Shelf    — A single cubby that holds one film box. Each shelf
#             is an open-front rectangular cell defined by its
#             inner width, height, and depth.
#
# Trapezoid — The tapered arm that extends forward from the
#             front edge of each shelf floor. Viewed from above,
#             it narrows from the full shelf width down to a
#             narrow tip (TRAP_TIP). This guides the film box
#             and provides a platform for the lip.
#
# Lip      — A small vertical wall at the tip of the trapezoid.
#             It prevents the film box from sliding out on its
#             own, while still allowing you to lift the box over
#             it easily.
#
# Scoop    — A semicircular cutout on each vertical wall of a
#             shelf, visible from the side profile. The chord
#             of the semicircle sits at the front edge of the
#             shelf, and the curve bites back into the wall.
#             This saves material and print time.
#
# PARAMETERS
# ----------
# WALL       — Thickness of vertical walls and the ceiling.
# SHELF_WALL — Thickness of horizontal shelves (floors). Kept
#              slightly thicker than WALL for structural strength
#              since they carry the weight of the film boxes and
#              support the trapezoid arms.
# RACK_DEPTH — How deep the rectangular shelf portion is (the
#              part of the box enclosed by walls on all sides).
# BACK_WALL  — Thickness of the solid back panel.
# OVERHANG   — How far the trapezoid arm extends forward past
#              the front edge of the shelf.
# SCOOP_RATIO — Size of the scoop as a fraction of shelf height
#              (e.g. 0.60 = scoop diameter is 60% of shelf height).
#
# PRINTING TIPS
# -------------
# - Print on its back (back wall flat on bed). Shelves become
#   vertical walls needing no support. The small lip overhangs
#   (~2-3mm) bridge fine without supports.
# - Use 3+ perimeters for wall strength at thin wall settings.
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

FILM_TYPE = "35mm"    # "35mm" or "120"
COLS      = 4
ROWS      = 5

# ============================================================
# Film-type-specific parameters
# ============================================================
FILM_PARAMS = {
    "35mm": {
        "RACK_DEPTH":  43.2,
        "LIP_HEIGHT":  4.0,
        "OVERHANG":    21.3,
        "SLOT_WIDTH":  40.0,
        "SLOT_HEIGHT": 42.0,
        "SCOOP_RATIO": 0.60,
    },
    "120": {
        "RACK_DEPTH":  50.0,
        "LIP_HEIGHT":  3.5,
        "OVERHANG":    32.6,
        "SLOT_WIDTH":  31.0,
        "SLOT_HEIGHT": 33.0,
        "SCOOP_RATIO": 0.80,
    },
}

if FILM_TYPE not in FILM_PARAMS:
    print(f"Unknown film type '{FILM_TYPE}'. Choose '35mm' or '120'.")
    sys.exit(1)

params = FILM_PARAMS[FILM_TYPE]
RACK_DEPTH  = params["RACK_DEPTH"]
LIP_HEIGHT  = params["LIP_HEIGHT"]
OVERHANG    = params["OVERHANG"]
SLOT_WIDTH  = params["SLOT_WIDTH"]
SLOT_HEIGHT = params["SLOT_HEIGHT"]
SCOOP_RATIO = params["SCOOP_RATIO"]

# ============================================================
# Shared parameters (same for both film types)
# ============================================================
WALL           = 1.3    # vertical walls and ceiling
SHELF_WALL     = 1.6    # horizontal shelves (floor + internal shelves)
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
print(f"Grid: {COLS} x {ROWS} = {COLS * ROWS} slots")
print(f"Rack: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"With overhang: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH + OVERHANG:.1f} x {TOTAL_HEIGHT:.1f} mm")

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
# Semicircular cutouts on all vertical walls
# ============================================================
scoop_r = SCOOP_RATIO * SLOT_HEIGHT / 2.0

cyl_template = trimesh.creation.cylinder(radius=scoop_r, height=WALL + 0.5, sections=SCOOP_SEGMENTS)
rot = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
cyl_template.apply_transform(rot)

front_cut_template = trimesh.creation.box(extents=[WALL + 2, scoop_r * 2 + 10, scoop_r * 2 + 10])

for row in range(ROWS):
    scoop_cz = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
    
    wall_positions = []
    wall_positions.append((WALL/2, WALL))
    wall_positions.append((TOTAL_WIDTH - WALL/2, WALL))
    for col in range(1, COLS):
        x = col * (SLOT_WIDTH + WALL) + WALL/2
        wall_positions.append((x, WALL))
    
    for wall_x, wall_w in wall_positions:
        cyl = cyl_template.copy()
        cyl.apply_translation([wall_x, 0, scoop_cz])
        
        front_cut = front_cut_template.copy()
        front_cut.apply_translation([wall_x, -(scoop_r + 5) - 0.1, scoop_cz])
        
        half_cyl = trimesh.boolean.difference([cyl, front_cut], engine='manifold')
        result = trimesh.boolean.difference([result, half_cyl], engine='manifold')

print("Shell with cutouts done")

# ============================================================
# Trapezoid arms + lips for each slot
# ============================================================
extras = []
for row in range(ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col in range(COLS):
        col_x_left  = col * (SLOT_WIDTH + WALL) + WALL
        col_x_right = col_x_left + SLOT_WIDTH
        slot_center = (col_x_left + col_x_right) / 2.0
        tip_left  = slot_center - TRAP_TIP / 2.0
        tip_right = slot_center + TRAP_TIP / 2.0
        
        trap_poly = Polygon([
            (col_x_left, 0),
            (col_x_right, 0),
            (tip_right, -OVERHANG),
            (tip_left, -OVERHANG),
        ])
        trap_mesh = trimesh.creation.extrude_polygon(trap_poly, height=SHELF_WALL)
        trap_mesh.apply_translation([0, 0, shelf_z])
        extras.append(trap_mesh)
        
        lip = trimesh.creation.box(extents=[TRAP_TIP, SHELF_WALL, LIP_HEIGHT])
        lip.apply_translation([slot_center, -OVERHANG + SHELF_WALL/2, shelf_z + SHELF_WALL + LIP_HEIGHT/2])
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
