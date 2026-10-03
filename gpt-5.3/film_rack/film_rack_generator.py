import trimesh
import numpy as np
from shapely.geometry import Polygon
import sys

# ============================================================
# Film Rack Generator — Composable Sections
# ============================================================
#
# Generates 3D-printable film storage racks. Supports single-
# section racks (one film type) and stacked multi-section racks
# that mix film types (e.g. 5-pack shelves on bottom, single
# 120 cubbies on top).
#
# SUPPORTED FILM TYPES
# --------------------
#   "35mm"       — 35mm film boxes (40mm cubbies)
#   "120"        — Single 120 medium format rolls (31mm cubbies)
#   "120-5pack"  — 120 five-pack boxes (138mm wide shelves)
#
# HOW TO CONFIGURE
# ----------------
# Edit the SECTIONS list below. Each section is a dict with:
#   "type" — one of the film types above
#   "rows" — number of rows in this section
#   "cols" — number of columns in this section
#
# SECTIONS are listed BOTTOM TO TOP. The first entry is the
# bottom section; the last is the top.
#
# Examples:
#   # Simple 4x5 35mm rack:
#   SECTIONS = [{"type": "35mm", "rows": 5, "cols": 4}]
#
#   # Hybrid: 2 rows of 120 5-packs on bottom, 3x4 120 singles on top:
#   SECTIONS = [
#       {"type": "120-5pack", "rows": 2, "cols": 1},
#       {"type": "120",       "rows": 3, "cols": 4},
#   ]
#
#   # Three-tier sampler with 35mm, 120 singles, and 120 5-packs:
#   SECTIONS = [
#       {"type": "120-5pack", "rows": 1, "cols": 1},
#       {"type": "120",       "rows": 3, "cols": 4},
#       {"type": "35mm",      "rows": 2, "cols": 3},
#   ]
#
# Narrower sections are centered horizontally over wider ones.
# Adjacent sections share a single-thickness divider (the upper
# section sinks into the lower by SHELF_WALL so the floor of one
# merges with the ceiling of the other).
#
# TERMINOLOGY
# -----------
# Rack      — The full assembled unit; may contain multiple sections.
# Section   — A horizontal band of shelves sharing one film type.
# Shelf     — A single cubby holding one item.
# Trapezoid — Tapered arm extending forward from each shelf floor.
# Lip       — Small vertical wall at the trapezoid tip.
# Scoop     — Semicircular cutout on each vertical wall.
#
# PRINTING: print on its back (back wall flat on bed).
# DEPS:     pip install trimesh manifold3d shapely numpy
#
# ============================================================
#
# USER SETTINGS — edit this list:
#

SECTIONS = [
    {"type": "35mm", "rows": 5, "cols": 2},
]

# ============================================================
# Film-type-specific parameters
# ============================================================

FILM_PROFILES = {
    "35mm": {
        "RACK_DEPTH":      43.2,
        "LIP_HEIGHT":      4.0,
        "OVERHANG":        21.3,
        "SLOT_WIDTH":      40.0,
        "SLOT_HEIGHT":     42.0,
        "SCOOP_RATIO":     0.60,
        "TRAP_BASE_WIDTH": None,   # None = full slot width
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
        "OVERHANG":        24.6,   # 8mm shorter than 120 single (was 32.6)
        "SLOT_WIDTH":      139.0,  # 1mm wider inner width (was 138.0)
        "SLOT_HEIGHT":     33.0,
        "SCOOP_RATIO":     0.80,
        "TRAP_BASE_WIDTH": 31.0,
        "TRAP_COUNT":      2,
    },
}

# ============================================================
# Shared parameters (same for all film types)
# ============================================================
WALL           = 1.3
SHELF_WALL     = 1.6
BACK_WALL      = 2.0
TRAP_TIP       = 5.0
SCOOP_SEGMENTS = 64


def outer_width(slot_width, cols):
    """Outer X dimension for a row of `cols` cubbies of `slot_width`."""
    return cols * slot_width + (cols + 1) * WALL


def section_height(slot_height, rows):
    """Outer Z dimension for a section with `rows` rows."""
    return rows * slot_height + (rows + 1) * SHELF_WALL


def build_section(film_type, rows, cols):
    """
    Build one complete rack section as a standalone mesh.
    The section sits with its bottom-front-left corner at (0, 0, 0).
    Y extends into positive (back wall at y = RACK_DEPTH + BACK_WALL).
    Trapezoids extend into negative Y (front of the mesh).
    """
    if film_type not in FILM_PROFILES:
        valid = ", ".join(f"'{k}'" for k in FILM_PROFILES)
        print(f"Unknown film type '{film_type}'. Choose from: {valid}.")
        sys.exit(1)

    p = FILM_PROFILES[film_type]
    RACK_DEPTH      = p["RACK_DEPTH"]
    LIP_HEIGHT      = p["LIP_HEIGHT"]
    OVERHANG        = p["OVERHANG"]
    SLOT_WIDTH      = p["SLOT_WIDTH"]
    SLOT_HEIGHT     = p["SLOT_HEIGHT"]
    SCOOP_RATIO     = p["SCOOP_RATIO"]
    TRAP_BASE_WIDTH = p["TRAP_BASE_WIDTH"] or SLOT_WIDTH
    TRAP_COUNT      = p["TRAP_COUNT"]

    outer_w = outer_width(SLOT_WIDTH, cols)
    outer_h = section_height(SLOT_HEIGHT, rows)
    outer_d = RACK_DEPTH + BACK_WALL

    # Outer shell
    shell = trimesh.creation.box(extents=[outer_w, outer_d, outer_h])
    shell.apply_translation([outer_w/2, outer_d/2, outer_h/2])

    # Cavities
    for row in range(rows):
        for col in range(cols):
            x_c = col * (SLOT_WIDTH + WALL) + WALL + SLOT_WIDTH/2
            z_c = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
            cav = trimesh.creation.box(extents=[SLOT_WIDTH, RACK_DEPTH + WALL + 1, SLOT_HEIGHT])
            cav.apply_translation([x_c, (RACK_DEPTH - 1)/2, z_c])
            shell = trimesh.boolean.difference([shell, cav], engine='manifold')

    # Scoops
    scoop_r = SCOOP_RATIO * SLOT_HEIGHT / 2.0
    cyl_t = trimesh.creation.cylinder(radius=scoop_r, height=WALL + 0.5, sections=SCOOP_SEGMENTS)
    rot = trimesh.transformations.rotation_matrix(np.pi/2, [0, 1, 0])
    cyl_t.apply_transform(rot)
    fc_t = trimesh.creation.box(extents=[WALL + 2, scoop_r*2 + 10, scoop_r*2 + 10])

    for row in range(rows):
        scz = row * (SLOT_HEIGHT + SHELF_WALL) + SHELF_WALL + SLOT_HEIGHT/2
        wall_xs = [WALL/2, outer_w - WALL/2]
        for c in range(1, cols):
            wall_xs.append(c * (SLOT_WIDTH + WALL) + WALL/2)

        for wx in wall_xs:
            cyl = cyl_t.copy()
            cyl.apply_translation([wx, 0, scz])
            fc = fc_t.copy()
            fc.apply_translation([wx, -(scoop_r + 5) - 0.1, scz])
            half = trimesh.boolean.difference([cyl, fc], engine='manifold')
            shell = trimesh.boolean.difference([shell, half], engine='manifold')

    # Trapezoids + lips
    extras = []
    for row in range(rows):
        shelf_z = row * (SLOT_HEIGHT + SHELF_WALL)
        for col in range(cols):
            sxl = col * (SLOT_WIDTH + WALL) + WALL
            gap = (SLOT_WIDTH - TRAP_COUNT * TRAP_BASE_WIDTH) / (TRAP_COUNT + 1)
            for i in range(TRAP_COUNT):
                cx = sxl + (i + 1) * gap + (i + 0.5) * TRAP_BASE_WIDTH
                bl = cx - TRAP_BASE_WIDTH/2
                br = cx + TRAP_BASE_WIDTH/2
                tl = cx - TRAP_TIP/2
                tr = cx + TRAP_TIP/2

                trap_poly = Polygon([(bl, 0), (br, 0), (tr, -OVERHANG), (tl, -OVERHANG)])
                tm = trimesh.creation.extrude_polygon(trap_poly, height=SHELF_WALL)
                tm.apply_translation([0, 0, shelf_z])
                extras.append(tm)

                lip = trimesh.creation.box(extents=[TRAP_TIP, SHELF_WALL, LIP_HEIGHT])
                lip.apply_translation([cx, -OVERHANG + SHELF_WALL/2,
                                       shelf_z + SHELF_WALL + LIP_HEIGHT/2])
                extras.append(lip)

    shell = trimesh.boolean.union([shell] + extras, engine='manifold')
    return shell


# ============================================================
# Build & stack all sections
# ============================================================

if not SECTIONS:
    print("SECTIONS list is empty.")
    sys.exit(1)

# Compute per-section dimensions for layout planning
section_widths  = []
section_heights = []
section_depths  = []
for sec in SECTIONS:
    p = FILM_PROFILES[sec["type"]]
    section_widths.append(outer_width(p["SLOT_WIDTH"], sec["cols"]))
    section_heights.append(section_height(p["SLOT_HEIGHT"], sec["rows"]))
    section_depths.append(p["RACK_DEPTH"] + BACK_WALL)

max_width = max(section_widths)

# Report
print("Sections (bottom to top):")
for i, sec in enumerate(SECTIONS):
    print(f"  [{i}] {sec['type']}: {sec['rows']} rows x {sec['cols']} cols "
          f"-> {section_widths[i]:.1f} x {section_depths[i]:.1f} x {section_heights[i]:.1f} mm")

total_height = sum(section_heights) - (len(SECTIONS) - 1) * SHELF_WALL
max_overhang = max(FILM_PROFILES[sec["type"]]["OVERHANG"] for sec in SECTIONS)
max_depth    = max(section_depths)
print(f"Assembled: {max_width:.1f} x {max_depth:.1f} x {total_height:.1f} mm")
print(f"With overhang: {max_width:.1f} x {max_depth + max_overhang:.1f} x {total_height:.1f} mm")

# Build & position each section
print("\nBuilding sections...")
meshes = []
z_cursor = 0.0   # where the current section's bottom sits

for i, sec in enumerate(SECTIONS):
    print(f"  Building section {i}: {sec['type']} {sec['rows']}x{sec['cols']}")
    m = build_section(sec["type"], sec["rows"], sec["cols"])
    # Center horizontally on max_width
    x_offset = (max_width - section_widths[i]) / 2.0
    # Align back walls: shift shallower sections back (+Y) by the depth difference
    # so every section's back wall sits at y = max_depth
    y_offset = max_depth - section_depths[i]
    m.apply_translation([x_offset, y_offset, z_cursor])
    meshes.append(m)
    # Next section's bottom sinks SHELF_WALL below this section's top to merge dividers
    z_cursor += section_heights[i] - SHELF_WALL

print("Unioning...")
if len(meshes) == 1:
    result = meshes[0]
else:
    result = trimesh.boolean.union(meshes, engine='manifold')

# ============================================================
# Save
# ============================================================
if len(SECTIONS) == 1:
    s = SECTIONS[0]
    out_path = f"film_rack_{s['type']}_{s['cols']}x{s['rows']}.stl"
else:
    parts = "_".join(f"{s['type']}-{s['cols']}x{s['rows']}" for s in SECTIONS)
    out_path = f"film_rack_hybrid_{parts}.stl"

result.export(out_path)
print(f"\nSaved to {out_path}")
print(f"Vertices: {len(result.vertices)}, Faces: {len(result.faces)}")
bounds = result.bounds
print(f"Size: {bounds[1] - bounds[0]}")
