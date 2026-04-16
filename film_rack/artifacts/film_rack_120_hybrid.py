import trimesh
import numpy as np
from shapely.geometry import Polygon

# ============================================================
# Hybrid 120 Film Rack Generator
# ============================================================
#
# A combination rack with two shelf types:
#
#   - 5-pack shelves (bottom): Wide cubbies sized to hold a
#     full 5-pack box of 120 film. Each gets two trapezoid
#     arms positioned at the 2nd and 4th column locations.
#
#   - Single cubbies (top): 5 columns of individual 120 roll
#     cubbies, each with its own trapezoid arm and lip.
#
# The rack is always 5 columns wide (fixed by the single
# cubby grid). The number of 5-pack rows and single cubby
# rows can be adjusted independently.
#
# See film_rack_generator.py for terminology (shelf, rack,
# trapezoid, lip, scoop).
#
# DEPENDENCIES: pip install trimesh manifold3d shapely numpy
#
# ============================================================
#
# USER SETTINGS — adjust these two values:
#

SINGLE_ROWS   = 3    # rows of individual 120 cubbies (top)
FIVEPACK_ROWS = 2    # rows of wide 5-pack shelves (bottom)

# ============================================================
# Fixed parameters (shared with single 120 cubby design)
# ============================================================

WALL       = 1.3
SHELF_WALL = 1.6
RACK_DEPTH = 50.0
BACK_WALL  = 2.0
LIP_HEIGHT = 3.5
TRAP_TIP   = 5.0
OVERHANG   = 32.6

SLOT_WIDTH  = 31.0    # single 120 cubby width
SLOT_HEIGHT = 33.0    # same for both single and 5-pack
SCOOP_RATIO = 0.80
SCOOP_SEGMENTS = 64

COLS = 5              # always 5 columns (determines overall width)
TOTAL_ROWS = SINGLE_ROWS + FIVEPACK_ROWS

# Derived dimensions
TOTAL_WIDTH  = COLS * SLOT_WIDTH + (COLS + 1) * WALL
TOTAL_HEIGHT = TOTAL_ROWS * SLOT_HEIGHT + (TOTAL_ROWS + 1) * SHELF_WALL
TOTAL_DEPTH  = RACK_DEPTH + BACK_WALL

# 5-pack interior width = full width minus two outer walls
FIVEPACK_WIDTH = TOTAL_WIDTH - 2 * WALL

# Trapezoid positions for 5-pack shelves: at column 2 and 4 centers (1-indexed)
# These are 0-indexed columns 1 and 3
FIVEPACK_TRAP_COLS = [1, 3]

# Verify column centers
def col_center_x(col_idx):
    """X center of a column (0-indexed)"""
    return col_idx * (SLOT_WIDTH + WALL) + WALL + SLOT_WIDTH / 2.0

print(f"Hybrid rack: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"With overhang: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH + OVERHANG:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"5-pack interior width: {FIVEPACK_WIDTH:.1f} mm")
print(f"Trap positions (col centers): {[col_center_x(c) for c in FIVEPACK_TRAP_COLS]}")
print(f"Total slots: {FIVEPACK_ROWS} wide + {SINGLE_ROWS * COLS} single = {FIVEPACK_ROWS + SINGLE_ROWS * COLS}")

# ============================================================
# Build outer shell
# ============================================================
outer = trimesh.creation.box(extents=[TOTAL_WIDTH, TOTAL_DEPTH, TOTAL_HEIGHT])
outer.apply_translation([TOTAL_WIDTH/2, TOTAL_DEPTH/2, TOTAL_HEIGHT/2])
result = outer

# ============================================================
# Cut cavities
# ============================================================

# Bottom rows (0 to FIVEPACK_ROWS-1): wide 5-pack cavities
for row in range(FIVEPACK_ROWS):
    z_center = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT / 2.0
    cavity = trimesh.creation.box(extents=[FIVEPACK_WIDTH, RACK_DEPTH + WALL + 1, SLOT_HEIGHT])
    cavity.apply_translation([TOTAL_WIDTH / 2.0, (RACK_DEPTH - 1) / 2, z_center])
    result = trimesh.boolean.difference([result, cavity], engine='manifold')

# Top rows (FIVEPACK_ROWS to TOTAL_ROWS-1): single cubby cavities
for row in range(FIVEPACK_ROWS, TOTAL_ROWS):
    for col in range(COLS):
        x_center = col_center_x(col)
        z_center = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT / 2.0
        cavity = trimesh.creation.box(extents=[SLOT_WIDTH, RACK_DEPTH + WALL + 1, SLOT_HEIGHT])
        cavity.apply_translation([x_center, (RACK_DEPTH - 1) / 2, z_center])
        result = trimesh.boolean.difference([result, cavity], engine='manifold')

print("Cavities cut")

# ============================================================
# Scoop cutouts on vertical walls
# ============================================================
scoop_r = SCOOP_RATIO * SLOT_HEIGHT / 2.0

cyl_template = trimesh.creation.cylinder(radius=scoop_r, height=WALL + 0.5, sections=SCOOP_SEGMENTS)
rot = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
cyl_template.apply_transform(rot)
front_cut_template = trimesh.creation.box(extents=[WALL + 2, scoop_r * 2 + 10, scoop_r * 2 + 10])

# Outer walls: scoops for ALL rows
for row in range(TOTAL_ROWS):
    scoop_cz = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT / 2.0
    
    for wall_x in [WALL / 2, TOTAL_WIDTH - WALL / 2]:
        cyl = cyl_template.copy()
        cyl.apply_translation([wall_x, 0, scoop_cz])
        front_cut = front_cut_template.copy()
        front_cut.apply_translation([wall_x, -(scoop_r + 5) - 0.1, scoop_cz])
        half_cyl = trimesh.boolean.difference([cyl, front_cut], engine='manifold')
        result = trimesh.boolean.difference([result, half_cyl], engine='manifold')

# Internal dividers: scoops only for SINGLE CUBBY rows
for row in range(FIVEPACK_ROWS, TOTAL_ROWS):
    scoop_cz = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT / 2.0
    
    for col in range(1, COLS):
        wall_x = col * (SLOT_WIDTH + WALL) + WALL / 2
        cyl = cyl_template.copy()
        cyl.apply_translation([wall_x, 0, scoop_cz])
        front_cut = front_cut_template.copy()
        front_cut.apply_translation([wall_x, -(scoop_r + 5) - 0.1, scoop_cz])
        half_cyl = trimesh.boolean.difference([cyl, front_cut], engine='manifold')
        result = trimesh.boolean.difference([result, half_cyl], engine='manifold')

print("Scoop cutouts done")

# ============================================================
# Add internal vertical dividers for single cubby rows only
# ============================================================
# The cavities already created the openings, but we need to make sure
# dividers exist. Since we cut individual cavities for the single rows,
# the material between them IS the divider — no extra step needed.
# But we need to verify the dividers only span the single cubby rows,
# not extending down into the 5-pack rows. The outer shell is solid,
# and we only cut individual cavities in the top rows, so the dividers
# are automatically correct. Good.

# ============================================================
# Trapezoid arms + lips
# ============================================================
extras = []

# Single cubby rows: one trapezoid per cubby
for row in range(FIVEPACK_ROWS, TOTAL_ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col in range(COLS):
        cx = col_center_x(col)
        col_x_left = col * (SLOT_WIDTH + WALL) + WALL
        col_x_right = col_x_left + SLOT_WIDTH
        tip_left = cx - TRAP_TIP / 2.0
        tip_right = cx + TRAP_TIP / 2.0
        
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
        lip.apply_translation([cx, -OVERHANG + SHELF_WALL / 2, shelf_z + SHELF_WALL + LIP_HEIGHT / 2])
        extras.append(lip)

# 5-pack rows: two trapezoids at column 2 and 4 positions (0-indexed 1 and 3)
for row in range(FIVEPACK_ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col_idx in FIVEPACK_TRAP_COLS:
        cx = col_center_x(col_idx)
        col_x_left = col_idx * (SLOT_WIDTH + WALL) + WALL
        col_x_right = col_x_left + SLOT_WIDTH
        tip_left = cx - TRAP_TIP / 2.0
        tip_right = cx + TRAP_TIP / 2.0
        
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
        lip.apply_translation([cx, -OVERHANG + SHELF_WALL / 2, shelf_z + SHELF_WALL + LIP_HEIGHT / 2])
        extras.append(lip)

print(f"Adding {len(extras)} trapezoids and lips")
result = trimesh.boolean.union([result] + extras, engine='manifold')

# ============================================================
# Save
# ============================================================
out_path = f"film_rack_hybrid_{FIVEPACK_ROWS}fp_{SINGLE_ROWS}x{COLS}single.stl"
result.export(out_path)
print(f"Saved to {out_path}")
print(f"Vertices: {len(result.vertices)}, Faces: {len(result.faces)}")
bounds = result.bounds
print(f"Size: {bounds[1] - bounds[0]}")
