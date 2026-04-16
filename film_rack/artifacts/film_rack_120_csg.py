import trimesh
import numpy as np
from shapely.geometry import Polygon

# ============================================================
# 120 Medium Format Film Box Rack — CSG approach
# ============================================================

WALL       = 1.3   # vertical walls and ceiling
SHELF_WALL = 1.6   # horizontal shelves (floor + internal shelves)
RACK_DEPTH = 50.0
BACK_WALL  = 2.0
LIP_HEIGHT = 3.5
TRAP_TIP   = 5.0
OVERHANG   = 32.6  # +1mm for longer trapezoid

SLOT_WIDTH  = 31.0
SLOT_HEIGHT = 33.0

COLS = 4
ROWS = 5

SCOOP_RATIO = 0.80
SCOOP_SEGMENTS = 64

TOTAL_WIDTH  = COLS * SLOT_WIDTH + (COLS + 1) * WALL
TOTAL_HEIGHT = ROWS * SLOT_HEIGHT + (ROWS + 1) * SHELF_WALL
TOTAL_DEPTH  = RACK_DEPTH + BACK_WALL

print(f"Rack: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"With overhang: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH + OVERHANG:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"Slots: {COLS} x {ROWS} = {COLS*ROWS}")

# --- Build outer shell with all cavities ---
outer = trimesh.creation.box(extents=[TOTAL_WIDTH, TOTAL_DEPTH, TOTAL_HEIGHT])
outer.apply_translation([TOTAL_WIDTH/2, TOTAL_DEPTH/2, TOTAL_HEIGHT/2])

result = outer

# Cut all slot cavities (open at front)
for row in range(ROWS):
    for col in range(COLS):
        x_center = col * (SLOT_WIDTH + WALL) + WALL + SLOT_WIDTH/2
        z_center = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
        
        cavity = trimesh.creation.box(extents=[SLOT_WIDTH, RACK_DEPTH + WALL + 1, SLOT_HEIGHT])
        cavity.apply_translation([x_center, (RACK_DEPTH - 1)/2, z_center])
        result = trimesh.boolean.difference([result, cavity], engine='manifold')

# --- Semicircular cutouts on all vertical walls ---
scoop_r = SCOOP_RATIO * SLOT_HEIGHT / 2.0

# Create the half-cylinder template once
cyl_template = trimesh.creation.cylinder(radius=scoop_r, height=WALL + 0.5, sections=SCOOP_SEGMENTS)
rot = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
cyl_template.apply_transform(rot)

# Cut plane template
front_cut_template = trimesh.creation.box(extents=[WALL + 2, scoop_r * 2 + 10, scoop_r * 2 + 10])

for row in range(ROWS):
    scoop_cz = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
    
    # All vertical wall X positions (outer walls + internal dividers)
    wall_positions = []
    
    # Left outer wall
    wall_positions.append((WALL/2, WALL))
    # Right outer wall
    wall_positions.append((TOTAL_WIDTH - WALL/2, WALL))
    # Internal dividers
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

# --- Trapezoid arms + lips for each slot ---
extras = []
for row in range(ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col in range(COLS):
        col_x_left  = col * (SLOT_WIDTH + WALL) + WALL
        col_x_right = col_x_left + SLOT_WIDTH
        slot_center = (col_x_left + col_x_right) / 2.0
        tip_left  = slot_center - TRAP_TIP / 2.0
        tip_right = slot_center + TRAP_TIP / 2.0
        
        # Trapezoid
        trap_poly = Polygon([
            (col_x_left, 0),
            (col_x_right, 0),
            (tip_right, -OVERHANG),
            (tip_left, -OVERHANG),
        ])
        trap_mesh = trimesh.creation.extrude_polygon(trap_poly, height=SHELF_WALL)
        trap_mesh.apply_translation([0, 0, shelf_z])
        extras.append(trap_mesh)
        
        # Lip
        lip = trimesh.creation.box(extents=[TRAP_TIP, SHELF_WALL, LIP_HEIGHT])
        lip.apply_translation([slot_center, -OVERHANG + SHELF_WALL/2, shelf_z + SHELF_WALL + LIP_HEIGHT/2])
        extras.append(lip)

print(f"Adding {len(extras)} trapezoids and lips")
result = trimesh.boolean.union([result] + extras, engine='manifold')

# --- Save ---
out_path = '/home/claude/film_rack_full_csg.stl'
result.export(out_path)
print(f"Saved to {out_path}")
print(f"Vertices: {len(result.vertices)}, Faces: {len(result.faces)}")
bounds = result.bounds
print(f"Size: {bounds[1] - bounds[0]}")
