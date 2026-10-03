"""7-day pill box with a sliding dovetail lid. See design.md for the brief.

Axes: X along the row (Monday at −X), Y front→back (front = −Y, day
letters), Z up. Origin: centre of the base's footprint, on its bottom face.
"""

from __future__ import annotations

from build123d import (Align, Axis, Box, Compound, FontStyle, Location, Plane,
                       Polygon, SlotOverall, Text, chamfer, extrude, fillet)

from common.geom import section
from common.model import Dim, Model, Note, Part, Sheet

# ---- the pill (Zoloft 100 mg), measured with calipers 2026-10-03
PILL_L, PILL_W, PILL_T = 13.0, 6.0, 5.0

# ---- design parameters (mm)
DAYS = "MTWTFSS"
POCKET_X = 11.0          # along the row
POCKET_Y = 17.0          # front to back; the pill lies this way
POCKET_D = 6.5           # floor to lid underside
POCKET_R_CORNER = 3.0    # vertical pocket corners
POCKET_R_FLOOR = 2.5     # pocket floor edge
DIVIDER = 1.2
END_WALL = 2.0
FLOOR = 1.2
SIDE_WALL = 2.0          # base outer face -> widest point of the lid slot
LID_T = 2.0
LID_UNDERCUT = 1.2       # dovetail: slot is this much wider per side at its bottom than its top
LID_CLEARANCE = 0.25     # horizontal running clearance per side; tune with the coupon
CORNER_R_MONDAY = 3.0    # outer vertical corners, closed end
CORNER_R_SUNDAY = 1.0    # open end: kept small so it doesn't break into the lid slot
BOTTOM_CHAMFER = 0.4     # elephant's-foot relief
LABEL_SIZE = 5.0
LABEL_DEPTH = 0.5
GRIP_GROOVES = 3
GRIP_W, GRIP_DEPTH, GRIP_PITCH = 1.2, 0.6, 2.6

# ---- derived
LID_Z = FLOOR + POCKET_D                       # lid underside / divider tops
H = LID_Z + LID_T
SLOT_TOP_W = POCKET_Y
SLOT_BOT_W = POCKET_Y + 2 * LID_UNDERCUT
W = SLOT_BOT_W + 2 * SIDE_WALL


def length(n: int) -> float:
    return 2 * END_WALL + n * POCKET_X + (n - 1) * DIVIDER


def pocket_x(i: int, n: int) -> float:
    return -length(n) / 2 + END_WALL + POCKET_X / 2 + i * (POCKET_X + DIVIDER)


def dovetail(half_bottom: float, half_top: float, x0: float, x1: float, extra_top: float = 0.0):
    """Dovetail prism from x0 to x1: bottom at LID_Z, top at H (+extra_top straight up)."""
    pts = [(-half_bottom, LID_Z), (half_bottom, LID_Z), (half_top, H)]
    if extra_top:
        pts += [(half_top, H + extra_top), (-half_top, H + extra_top)]
    pts += [(-half_top, H)]
    return extrude(Plane.YZ.offset(x0) * Polygon(*pts, align=None), amount=x1 - x0)


def build_base(n: int):
    L = length(n)
    base = Box(L, W, H, align=(Align.CENTER, Align.CENTER, Align.MIN))
    vertical = base.edges().filter_by(Axis.Z)
    base = fillet(vertical.filter_by(lambda e: e.center().X < 0), CORNER_R_MONDAY)
    base = fillet(base.edges().filter_by(Axis.Z).filter_by(lambda e: e.center().X > 0), CORNER_R_SUNDAY)
    base = chamfer(base.edges().group_by(Axis.Z)[0], BOTTOM_CHAMFER)

    tool = Box(POCKET_X, POCKET_Y, POCKET_D + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    tool = fillet(tool.edges().filter_by(Axis.Z), POCKET_R_CORNER)
    tool = fillet(tool.edges().group_by(Axis.Z)[0], POCKET_R_FLOOR)
    for i in range(n):
        base -= tool.moved(Location((pocket_x(i, n), 0, FLOOR)))

    base -= dovetail(SLOT_BOT_W / 2, SLOT_TOP_W / 2, -L / 2 + END_WALL, L / 2 + 1, extra_top=1)

    for i in range(n):
        face = Plane(origin=(pocket_x(i, n), -W / 2, (FLOOR + LID_Z) / 2), x_dir=(1, 0, 0), z_dir=(0, -1, 0))
        letter = Text(DAYS[i % 7], font_size=LABEL_SIZE, font_style=FontStyle.BOLD)
        base -= extrude(face * letter, amount=-LABEL_DEPTH)
    return base


def build_lid(n: int):
    L = length(n)
    c = LID_CLEARANCE
    x0 = -L / 2 + END_WALL + c
    lid = dovetail(SLOT_BOT_W / 2 - c, SLOT_TOP_W / 2 - c, x0, L / 2)

    groove = Box(GRIP_W, SLOT_TOP_W - 5, GRIP_DEPTH + 1, align=(Align.CENTER, Align.CENTER, Align.MIN))
    for k in range(GRIP_GROOVES):
        lid -= groove.moved(Location((x0 + 4 + k * GRIP_PITCH, 0, H - GRIP_DEPTH)))
    ax = x0 + 4 + GRIP_GROOVES * GRIP_PITCH + 1.5          # arrow pointing towards Sunday (+X)
    arrow = Plane.XY.offset(H - GRIP_DEPTH) * Polygon((ax, -3.5), (ax + 5, 0), (ax, 3.5), align=None)
    lid -= extrude(arrow, amount=GRIP_DEPTH + 1)
    return lid


def build_pill(x: float):
    """Oblong tablet envelope, lying front-to-back on the pocket floor."""
    pill = extrude(SlotOverall(PILL_L, PILL_W, rotation=90), amount=PILL_T)
    pill = fillet(pill.edges().group_by(Axis.Z)[0] + pill.edges().group_by(Axis.Z)[-1], PILL_T * 0.4)
    return pill.moved(Location((x, 0, FLOOR)))


def build(variant: str = "full") -> Model:
    n = {"full": 7, "coupon": 2}[variant]  # coupon: two pockets so the lid is long enough to slide straight
    L = length(n)
    pill_at = pocket_x(n // 2, n)                       # Thursday: the cutaway plane goes through it
    base, lid = build_base(n), build_lid(n)
    parts = [
        Part("base", base, color="#ece6d8"),
        Part("lid", lid, color="#7fa7c9", explode=(0, 0, 14)),
        Part("pill", build_pill(pill_at), color="#f0cf3a", reference=True, explode=(0, 0, 4)),
    ]

    x0, x1 = pocket_x(0, n), pocket_x(min(1, n - 1), n)
    sheets = [
        Sheet("base", dims=[
            Dim("front", (-L / 2, 0, 0), (L / 2, 0, 0), "h", -10),
            Dim("front", (-L / 2, 0, 0), (-L / 2, 0, LID_Z), "v", -8),
            Dim("front", (-L / 2, 0, 0), (-L / 2, 0, H), "v", -16),
            Dim("top", (x0 - POCKET_X / 2, POCKET_Y / 2, H), (x0 + POCKET_X / 2, POCKET_Y / 2, H), "h", 8),
            *([Dim("top", (x0 + POCKET_X / 2, POCKET_Y / 2, H), (x1 - POCKET_X / 2, POCKET_Y / 2, H), "h", 16)]
              if n > 1 else []),
            Dim("top", (L / 2, -W / 2, H), (L / 2, W / 2, H), "v", 8),
            Dim("right", (L / 2, -SLOT_TOP_W / 2, H), (L / 2, SLOT_TOP_W / 2, H), "h", 8),
            Dim("right", (L / 2, -SLOT_BOT_W / 2, LID_Z), (L / 2, SLOT_BOT_W / 2, LID_Z), "h", 16),
            Dim("right", (L / 2, -W / 2, 0), (L / 2, W / 2, 0), "h", -10),
            Dim("right", (L / 2, W / 2, LID_Z), (L / 2, W / 2, H), "v", 8),
        ], notes=[
            Note("top", (x0, 0, H), f"{n}× pocket {POCKET_X:g} × {POCKET_Y:g}, {POCKET_D:g} deep\n"
                                    f"corners R{POCKET_R_CORNER:g}, floor edge R{POCKET_R_FLOOR:g}", side="above", along=40),
            Note("front", (x0, -W / 2, (FLOOR + LID_Z) / 2 + 1.5),
                 f"day letters {LABEL_DEPTH:g} deep", side="below", along=30),
        ]),
        Sheet("lid", dims=[
            Dim("front", (-L / 2 + END_WALL + LID_CLEARANCE, 0, LID_Z), (L / 2, 0, LID_Z), "h", -10),
            Dim("front", (L / 2, 0, LID_Z), (L / 2, 0, H), "v", 8),
            Dim("right", (L / 2, -(SLOT_TOP_W / 2 - LID_CLEARANCE), H), (L / 2, SLOT_TOP_W / 2 - LID_CLEARANCE, H), "h", 8),
            Dim("right", (L / 2, -(SLOT_BOT_W / 2 - LID_CLEARANCE), LID_Z),
                (L / 2, SLOT_BOT_W / 2 - LID_CLEARANCE, LID_Z), "h", -10),
        ], notes=[
            Note("top", (-L / 2 + END_WALL + LID_CLEARANCE + 4, 0, H),
                 f"{GRIP_GROOVES}× grip groove {GRIP_W:g} wide, {GRIP_DEPTH:g} deep", side="above", along=20),
            Note("top", (-L / 2 + END_WALL + LID_CLEARANCE + 4 + GRIP_GROOVES * GRIP_PITCH + 4, 0, H),
                 "arrow: slide towards Sunday", side="below", along=20),
        ]),
    ]
    return Model(name="pill_box", title="7-day pill box" + (" — fit coupon" if variant == "coupon" else ""),
                 parts=parts, sheets=sheets, checks=lambda r, p: checks(r, p, n),
                 section=Plane.YZ.offset(pill_at))


def checks(report, parts, n: int):
    base, lid, pill = parts["base"].shape, parts["lid"].shape, parts["pill"].shape
    L = length(n)

    # pockets, measured from a horizontal slice through the pocket walls (above the floor fillet)
    faces = section(base, Plane.XY.offset(FLOOR + POCKET_D - 1))
    holes = sorted((w.bounding_box() for f in faces for w in f.inner_wires()), key=lambda b: b.min.X)
    report.check("pocket count", len(holes) == n, f"{len(holes)} pockets in slice")
    for i, hb in enumerate(holes):
        report.dim(f"pocket {DAYS[i % 7]} size X", hb.size.X, POCKET_X)
        report.dim(f"pocket {DAYS[i % 7]} size Y", hb.size.Y, POCKET_Y)
    gaps = [b.min.X - a.max.X for a, b in zip(holes, holes[1:])]
    if gaps:
        report.dim("thinnest divider", min(gaps), DIVIDER)
    if holes:
        report.dim("Monday end wall", holes[0].min.X + L / 2, END_WALL)

    # floor thickness: walk up the pocket's centre line
    hits = sorted(p.Z for p, _ in base.find_intersection_points(Axis((pocket_x(0, n), 0, -1), (0, 0, 1))))
    report.dim("floor thickness", hits[1] - hits[0], FLOOR)

    # thinnest wall beside the lid slot: a ray across the box just above the ledge
    hits = sorted(p.Y for p, _ in base.find_intersection_points(Axis((0, -W, LID_Z + 0.05), (0, 1, 0))))
    report.dim("wall beside lid slot", hits[1] - hits[0], SIDE_WALL, tol=0.1)

    # lid fit: real booleans and distances, not parameter arithmetic
    report.check("lid/base: no interference", (base & lid).volume < 1e-6,
                 f"overlap {(base & lid).volume:.4f} mm³")
    def angled(shape):  # the dovetail faces: tilted, neither vertical nor horizontal
        return Compound([f for f in shape.faces() if abs(f.normal_at().Y) > 0.3 and abs(f.normal_at().Z) > 0.3])
    gap = angled(lid).distance_to(angled(base))
    report.check("lid running clearance", 0.15 <= gap <= 0.35, f"{gap:.3f} mm normal to the dovetail faces")
    report.check("lid can't lift out", (base & lid.moved(Location((0, 0, 0.5)))).volume > 1,
                 "lifting it 0.5 mm collides with the dovetail")
    report.check("lid stops at Monday end", (base & lid.moved(Location((-0.5, 0, 0)))).volume > 0.1,
                 "pushing it 0.5 mm towards Monday collides with the end wall")
    report.check("lid slides out at Sunday end", (base & lid.moved(Location((L * 0.6, 0, 0)))).volume < 1e-6)

    # the pill
    report.check("pill sits in pocket", (base & pill).volume < 1e-6,
                 f"overlap {(base & pill).volume:.4f} mm³ (pill {PILL_L}×{PILL_W}×{PILL_T})")
    report.at_least("headroom above pill", LID_Z - pill.bounding_box().max.Z, 1.0)
    report.check("pill clear of lid", (lid & pill).volume < 1e-6)
