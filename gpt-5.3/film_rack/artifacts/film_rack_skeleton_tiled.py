import trimesh
import numpy as np
from shapely.geometry import Polygon

# ============================================================
# Skeletonized tiled 35mm Film Box Rack
# ============================================================

WALL       = 1.3
SHELF_WALL = 1.6
RACK_DEPTH = 43.2
BACK_WALL  = 2.0
LIP_HEIGHT = 4.0
TRAP_TIP   = 5.0
OVERHANG   = 21.3

SLOT_WIDTH  = 40.0
SLOT_HEIGHT = 42.0

COLS = 1
ROWS = 1

SCOOP_RATIO = 0.60
SCOOP_SEGMENTS = 64

TOTAL_WIDTH  = COLS * SLOT_WIDTH + (COLS + 1) * WALL
TOTAL_HEIGHT = ROWS * SLOT_HEIGHT + (ROWS + 1) * SHELF_WALL
TOTAL_DEPTH  = RACK_DEPTH + BACK_WALL

cut_width  = SCOOP_RATIO * SLOT_WIDTH
cut_height = SCOOP_RATIO * SLOT_HEIGHT

print(f"Rack: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"With overhang: {TOTAL_WIDTH:.1f} x {TOTAL_DEPTH + OVERHANG:.1f} x {TOTAL_HEIGHT:.1f} mm")
print(f"Slots: {COLS} x {ROWS} = {COLS*ROWS}")

# ============================================================
# Build solid shell with cavities
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

print("Cavities cut")

# ============================================================
# Add trapezoid arms + lips FIRST (before skeleton cuts)
# ============================================================
extras = []
for row in range(ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col in range(COLS):
        col_x_left = col * (SLOT_WIDTH + WALL) + WALL
        col_x_right = col_x_left + SLOT_WIDTH
        slot_center_x = (col_x_left + col_x_right) / 2.0
        tip_left = slot_center_x - TRAP_TIP / 2.0
        tip_right = slot_center_x + TRAP_TIP / 2.0
        
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
        lip.apply_translation([slot_center_x, -OVERHANG + SHELF_WALL/2, shelf_z + SHELF_WALL + LIP_HEIGHT/2])
        extras.append(lip)

print(f"Adding {len(extras)} trapezoids and lips")
result = trimesh.boolean.union([result] + extras, engine='manifold')

# ============================================================
# NOW do skeleton cutouts (after trapezoids are part of the mesh)
# ============================================================

# --- Horizontal shelf cutouts (floor of each row) ---
for row in range(ROWS):
    shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
    for col in range(COLS):
        col_x_left = col * (SLOT_WIDTH + WALL) + WALL
        slot_center_x = col_x_left + SLOT_WIDTH / 2.0

        # Floor cutout through shelf only (stop at y=0, don't cut into trapezoid)
        floor_cut = trimesh.creation.box(extents=[cut_width, TOTAL_DEPTH, SHELF_WALL + 0.2])
        floor_cut.apply_translation([slot_center_x, TOTAL_DEPTH/2, shelf_z + SHELF_WALL/2])
        result = trimesh.boolean.difference([result, floor_cut], engine='manifold')

        # Trapezoid cutout — tapered, stopping 30% before lip
        trap_cutout_end = -OVERHANG * 0.70
        
        cut_x_left = slot_center_x - cut_width / 2.0
        cut_x_right = slot_center_x + cut_width / 2.0
        
        # At the cutout end point, compute where the main trapezoid edges are
        # Main trapezoid: center stays at slot_center_x
        # Half-width goes from SLOT_WIDTH/2 at y=0 to TRAP_TIP/2 at y=-OVERHANG
        taper_frac = (-trap_cutout_end) / OVERHANG  # how far along the taper (0.70)
        half_width_at_end = SLOT_WIDTH/2 + (TRAP_TIP/2 - SLOT_WIDTH/2) * taper_frac
        
        # Scale the cutout proportionally: cutout is cut_width/SLOT_WIDTH of the full width
        cut_ratio = cut_width / SLOT_WIDTH
        half_cut_at_end = half_width_at_end * cut_ratio
        
        gap_end_left = slot_center_x - half_cut_at_end
        gap_end_right = slot_center_x + half_cut_at_end
        
        gap_trap_poly = Polygon([
            (cut_x_left, 1.0),            # extend into shelf to ensure seamless join
            (cut_x_right, 1.0),
            (gap_end_right, trap_cutout_end),
            (gap_end_left, trap_cutout_end),
        ])
        gap_trap_mesh = trimesh.creation.extrude_polygon(gap_trap_poly, height=SHELF_WALL + 0.2)
        gap_trap_mesh.apply_translation([0, 0, shelf_z - 0.1])
        result = trimesh.boolean.difference([result, gap_trap_mesh], engine='manifold')

# Top ceiling cutouts
ceil_z = TOTAL_HEIGHT - SHELF_WALL
for col in range(COLS):
    slot_center_x = col * (SLOT_WIDTH + WALL) + WALL + SLOT_WIDTH / 2.0
    ceil_cut = trimesh.creation.box(extents=[cut_width, TOTAL_DEPTH + 1, SHELF_WALL + 0.2])
    ceil_cut.apply_translation([slot_center_x, TOTAL_DEPTH/2 - 0.5, ceil_z + SHELF_WALL/2])
    result = trimesh.boolean.difference([result, ceil_cut], engine='manifold')

print("Shelf skeleton cuts done")

# --- Vertical wall cutouts ---
for row in range(ROWS):
    side_center_z = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT / 2.0
    
    wall_x_positions = [WALL/2, TOTAL_WIDTH - WALL/2]
    for col in range(1, COLS):
        wall_x_positions.append(col * (SLOT_WIDTH + WALL) + WALL/2)
    
    for wall_x in wall_x_positions:
        wall_cut = trimesh.creation.box(extents=[WALL + 0.2, TOTAL_DEPTH + 1, cut_height])
        wall_cut.apply_translation([wall_x, TOTAL_DEPTH/2 - 0.5, side_center_z])
        result = trimesh.boolean.difference([result, wall_cut], engine='manifold')

print("Wall skeleton cuts done")

# --- Back wall cutouts ---
for row in range(ROWS):
    side_center_z = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT / 2.0
    for col in range(COLS):
        slot_center_x = col * (SLOT_WIDTH + WALL) + WALL + SLOT_WIDTH / 2.0
        back_cut = trimesh.creation.box(extents=[cut_width, BACK_WALL + 0.2, cut_height])
        back_cut.apply_translation([slot_center_x, TOTAL_DEPTH - BACK_WALL/2, side_center_z])
        result = trimesh.boolean.difference([result, back_cut], engine='manifold')

print("Back wall skeleton cuts done")

# ============================================================
# Save
# ============================================================
out_path = '/home/claude/film_rack_skeleton_tiled.stl'
result.export(out_path)
print(f"Saved to {out_path}")
print(f"Vertices: {len(result.vertices)}, Faces: {len(result.faces)}")
bounds = result.bounds
print(f"Size: {bounds[1] - bounds[0]}")
