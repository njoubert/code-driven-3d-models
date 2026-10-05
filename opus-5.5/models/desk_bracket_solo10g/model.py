"""Under-desk cradle for a Sonnet Solo10G (Thunderbolt 3 to 10 GbE). `cradle` is the part; `coupon`
is its fit test, cut out of it. See design.md.

Axes: X = left→right, Y = front→back (front = −Y: the Ethernet jack; Thunderbolt at +Y), Z = up.
The desk underside is z = 0; the cradle and the device (upside down) hang below it.
"""

from __future__ import annotations

from build123d import Align, Axis, Box, Location, Plane, Polygon, extrude, fillet

from common.fit import face_coverage, lift_to_clear, overlap, play, union
from common.geom import prism, profile
from common.model import Dim, Model, Note, Part, Sheet
from common.screws import CSK_ANGLE, CSK_D, SCREW_HEAD, SCREW_L, countersunk, screw

C, MIN, MAX = Align.CENTER, Align.MIN, Align.MAX

# ---- the device, measured with calipers (owner). Height: base plate to the top fins' tips; depth: front
# plate to back plate. The plates' screw heads stand 1.5 mm proud (102.1 over them) but sit in the open
# between the lips and the top bars (owner, from the first test print), so the lips fit the plates
DEV_W, DEV_H, DEV_D = 79.6, 24.6, 99.1
DEV_MASS = 0.24                # kg, published
JACK_TOP, JACK_BOTTOM = 4.9, 16.9   # RJ45 jack on the front, centred: its edges, down from the device's top (measured)
JACK_W = 16.0                  # **assumed**
TB_ABOVE_BASE = 7.6            # Thunderbolt port on the back, centred: its bottom edge above the base (measured)
TB_W, TB_H = 8.4, 2.6          # USB-C opening, **assumed** (standard)
# fins run front to back (owner). Their depth and pitch and the end plates are **assumed**, for the views
FIN_DEPTH, FIN_PITCH, FIN_GROOVE = 2.0, 4.0, 2.0
TOP_FINS, SIDE_FINS = 18, 5    # grooves between fins
END_PLATE = 4.0
# plugs, **assumed**: (width, height, length out of the device)
RJ45_PLUG = (14.0, 12.0, 40.0)  # plug and boot, centred on the jack
TB_PLUG = (12.0, 6.5, 30.0)     # moulding, centred on the port

# ---- mounting: upside down, base plate towards the desk
DESK_GAP = 5.0                 # air between the base plate and the desk (owner)
CLR = 0.2                      # per side, across: as the OWC cradle, which fit
CLR_Y = 0.2                    # per end, device to lips

# ---- the cradle
T = 6.0                        # posts, floor bars, floor rails. Was 4: a 4 × 4 floor rail (~15 mm², its corner
                               # rounded) broke off in test fitting. Printed standing on end, a rail's layers stack
                               # along its length, so bending it pulls them apart
RAIL_MIN_AREA = 30.0           # floor rail cross-section, at least twice the one that broke
TF = 4.0                       # flanges and side strips: a flat frame, STANDOFF under the desk
STANDOFF = 3.0                 # the side frame stands off the desk on four screw pads: the air pocket over the device
                               # vents through the slot this leaves along each side (owner: the pocket was sealed)
FLANGE = 16.0                  # flange reach beyond the side wall
HOLD = 8.0                     # how far the end frames (posts, floor bars) reach along the device from its ends
STOP_T = 4.0                   # lip and top bar thickness along Y. Was 2.5: owner worried the top bars would snap
                               # when the supports come off
LIP = 4.0                      # lips: reach up the device's end faces, full width. Below the Ethernet jack (4.9 up),
                               # so no notch (owner). Lifted any higher, the device's top edge meets the top bars
JACK_MARGIN = 0.5              # least room between the lip and the Ethernet plug
WINDOW_R = 6.0                 # side windows' corners (gussets between posts, flanges and floor rails; was 4)
R_FLANGE = 4.0                 # outer curve from flange to wall
R_FLOOR = 2.5                  # outer bottom corners
DESK_T = 18.0                  # reference desk

PETG = "PETG"                  # the project file loads the PLA preset: switch filament

# ---- coupon: the cradle's bottom, to test the fit before the full print
COUPON_WALL = 10.0             # kept above the floor bars' top: lips, posts' lower ends
COUPON_DEVICE = 15.0           # how much of the device the views show

# ---- derived: the cradle's key coordinates
XI = DEV_W / 2 + CLR           # inner face of the side walls (posts)
XO = XI + T                    # outer face
XF = XO + FLANGE               # flange edge
YI = DEV_D / 2 + CLR_Y         # inner face of the lips
Y1 = YI + STOP_T               # the cradle's ends
YH = YI - HOLD                 # where the end frames stop, along the device
Z_DEV_TOP = -DESK_GAP          # the device's base plate (upside down: on top)
Z_FLOOR = Z_DEV_TOP - DEV_H    # floor bars' top: the device's fin tips rest here
Z_BOTTOM = Z_FLOOR - T
Z_TOP = -STANDOFF              # the frame's top face: the pads span from here to the desk
Z_FRAME = Z_TOP - TF           # the frame's underside: screw heads seat here


def cradle_screws():
    """One screw in each flange, through the pad above each post."""
    xs, ys = XO + FLANGE / 2 + 1, (Y1 + YH) / 2
    return [(sx * xs, sy * ys) for sx in (-1, 1) for sy in (-1, 1)]


def make_cradle():
    """The U-profile (flanges, side walls, floor) runs the full length; between the end frames the
    side walls and the floor are cut away, leaving the flanges on top and a rail under each wall.
    A lip and a top bar across each end. The top frame stands off the desk on a pad above each post."""
    u = profile([(-XF, Z_TOP), (XF, Z_TOP), (XF, Z_FRAME), (XO, Z_FRAME), (XO, Z_BOTTOM), (-XO, Z_BOTTOM),
                 (-XO, Z_FRAME), (-XF, Z_FRAME)],
                holes=[(-XI, Z_FLOOR, XI, 1)],      # inner corners square: the device's edges are sharp
                corners=[(s * XO, Z_BOTTOM, R_FLOOR) for s in (-1, 1)]
                + [(s * XO, Z_FRAME, R_FLANGE) for s in (-1, 1)] + [(s * XF, Z_FRAME, 2) for s in (-1, 1)])
    cradle = prism(u, -Y1, Y1)
    # side windows: wall from the floor rail up to the flange, between the posts, corners rounded. Wide
    # enough to take the flange-to-wall curve with it: that stays on the posts only
    window = Box(2 * (XO + R_FLANGE + 1), 2 * YH, Z_FRAME - Z_FLOOR, align=(C, C, MIN)).moved(Location((0, 0, Z_FLOOR)))
    cradle -= fillet(window.edges().filter_by(Axis.X), WINDOW_R)
    # floor window: between the floor bars, inside the rails
    cradle -= Box(2 * XI, 2 * YH, T + 2, align=(C, C, MAX)).moved(Location((0, 0, Z_FLOOR + 1)))
    # lips (1 mm into each wall: one solid), and top bars from the desk down to the frame's underside, pad to
    # pad. Together they hold the device front to back: sitting on the floor bars, the lips stop it; lifted,
    # its top edge meets the top bars. The top bars also close each end frame at the top. They reach the desk
    # (owner: sturdier than a bar only as deep as the frame), so the pocket vents out of the sides only.
    for sy in (-1, 1):
        cradle += Box(2 * XI + 2, STOP_T, LIP, align=(C, MIN if sy < 0 else MAX, MIN)).moved(Location((0, sy * Y1, Z_FLOOR)))
        cradle += Box(2 * XI + 2, STOP_T, -Z_FRAME, align=(C, MIN if sy < 0 else MAX, MAX)).moved(Location((0, sy * Y1, 0)))
    # the pads: the end frames' footprint on the strip and flange, up to the desk. Only they touch it. Their
    # inner ends slope at 45° down into the frame: printed standing on the front end, the back pads build
    # up out of the flange without supports, and every pad runs into the frame instead of sitting on it
    over = STANDOFF + 0.5                          # down to 0.5 mm into the frame: one solid
    pad = Polygon((Y1, 0), (YH, 0), (YH - over, -over), (Y1, -over), align=None)
    for sx in (-1, 1):
        side = Plane(origin=(XI if sx > 0 else -XF, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))   # local (u, v) = (y, z)
        for sy in (-1, 1):
            block = extrude(side * pad, amount=XF - XI, dir=(1, 0, 0))
            cradle += block if sy > 0 else block.mirror(Plane.XZ)
    for x, y in cradle_screws():
        cradle -= countersunk(x, y, Z_FRAME, STANDOFF + TF)
    return cradle


def make_device():
    """Upside down: base plate up, DESK_GAP below the desk; top fins down, resting on the floor bars.
    Fins (assumed) run front to back between the end plates. The jack and port are cut in for the views."""
    body = Box(DEV_W, DEV_D, DEV_H, align=(C, C, MIN)).moved(Location((0, 0, Z_FLOOR)))
    run = DEV_D - 2 * END_PLATE
    grooves = [Box(FIN_GROOVE, run, FIN_DEPTH, align=(C, C, MIN)).moved(
        Location(((i - (TOP_FINS - 1) / 2) * FIN_PITCH, 0, Z_FLOOR))) for i in range(TOP_FINS)]
    zc = Z_FLOOR + DEV_H / 2
    for sx in (-1, 1):
        grooves += [Box(2 * FIN_DEPTH, run, FIN_GROOVE).moved(
            Location((sx * DEV_W / 2, 0, zc + (i - (SIDE_FINS - 1) / 2) * FIN_PITCH))) for i in range(SIDE_FINS)]
    body -= union(grooves)
    jack_z0, jack_z1 = Z_FLOOR + JACK_TOP, Z_FLOOR + JACK_BOTTOM      # the device's top is down
    body -= Box(JACK_W, 12, jack_z1 - jack_z0, align=(C, MIN, MIN)).moved(Location((0, -DEV_D / 2 - 1, jack_z0)))
    body -= Box(TB_W, 6, TB_H, align=(C, MAX, MAX)).moved(Location((0, DEV_D / 2 + 1, Z_DEV_TOP - TB_ABOVE_BASE)))
    return body


def make_plugs():
    """The Ethernet plug out of the front, the Thunderbolt plug out of the back. -> (rj45, tb)"""
    w, h, length = RJ45_PLUG
    rj45 = Box(w, length, h, align=(C, MAX, C)).moved(
        Location((0, -DEV_D / 2, Z_FLOOR + (JACK_TOP + JACK_BOTTOM) / 2)))
    w, h, length = TB_PLUG
    tb = Box(w, length, h, align=(C, MIN, C)).moved(
        Location((0, DEV_D / 2, Z_DEV_TOP - TB_ABOVE_BASE - TB_H / 2)))
    return rj45, tb


def desk():
    return Box(2 * XF + 40, 2 * Y1 + 60, DESK_T, align=(C, C, MIN))


def cradle_concept():
    cradle, device = make_cradle(), make_device()
    rj45, tb = make_plugs()
    stand = Location((0, 0, 0), (90, 0, 0))        # print standing on its front end
    parts = [
        Part("cradle", cradle, color="#e07a3f", print_pose=stand),
        Part("device", device, color="#5b6068", reference=True, explode=(0, 0, -30)),
        Part("rj45", rj45, color="#3a6fd8", reference=True),
        Part("thunderbolt", tb, color="#3a6fd8", reference=True),
        Part("screws", union([screw(x, y, Z_FRAME) for x, y in cradle_screws()]), color="#b8bcc2", reference=True),
        Part("desk", desk(), color="#c8a978", reference=True, opacity=0.25),
    ]
    sheets = [Sheet("cradle", material=PETG, dims=[
        Dim("front", (-XI, -Y1, Z_FLOOR), (XI, -Y1, Z_FLOOR), "h", -16),
        Dim("front", (-XF, -Y1, 0), (XF, -Y1, 0), "h", 8),
        Dim("front", (XO, -Y1, Z_BOTTOM), (XO, -Y1, 0), "v", 8),
        Dim("right", (XO, -YI, Z_FLOOR), (XO, YI, Z_FLOOR), "h", -16),
        Dim("right", (XO, -Y1, Z_FLOOR), (XO, -Y1, Z_FLOOR + LIP), "v", -8),
        Dim("right", (XF, 0, Z_TOP), (XF, Y1, 0), "v", 8),
        Dim("right", (XO, -Y1, Z_FRAME), (XO, -Y1, 0), "v", -8),
    ], notes=[Note("top", (XO + FLANGE / 2 + 1, -(Y1 + YH) / 2, 0),
                   f"{len(cradle_screws())}× countersunk for #6 flat-head screws, through the pads", side="right", along=0),
              Note("right", (XO, -Y1, Z_FLOOR + LIP), f"lips {LIP:g} high, full width, front and back",
                   side="above", along=-10),
              Note("right", (XO, Y1, Z_FRAME), f"top bars {-Z_FRAME:g} high, to the desk; {-Z_FRAME - DESK_GAP:g} over the device's ends",
                   side="above", along=0)])]
    detail = ("front lip under the Ethernet plug", (0, -Y1, Z_FLOOR + 6), 22)
    return parts, sheets, Plane.YZ, "Solo10G desk bracket — cradle (upside down, 5 mm under the desk)", detail


def coupon_concept():
    """Fit test: the cradle's bottom, cut straight out of it (floor bars and rails, lips, the posts' lower
    ends), so every surface the device touches is the cradle's own. Printed flat, as used."""
    keep = lambda z0, z1: Box(2 * XF + 10, 2 * Y1 + 10, z1 - z0, align=(C, C, MIN)).moved(Location((0, 0, z0)))
    coupon = make_cradle() & keep(Z_BOTTOM - 1, Z_FLOOR + COUPON_WALL)
    device = make_device() & keep(Z_FLOOR - 1, Z_FLOOR + COUPON_DEVICE)
    rj45, _ = make_plugs()
    parts = [
        Part("coupon", coupon, color="#e07a3f"),
        Part("device", device, color="#5b6068", reference=True, opacity=0.6, explode=(0, 0, 30)),
        Part("rj45", rj45, color="#3a6fd8", reference=True),
    ]
    sheets = [Sheet("coupon", material=PETG, dims=[
        Dim("top", (-XI, 0, Z_FLOOR), (XI, 0, Z_FLOOR), "h", 8),
        Dim("top", (XI, -YI, Z_FLOOR), (XI, YI, Z_FLOOR), "v", 8),
        Dim("right", (XO, -Y1, Z_FLOOR), (XO, -Y1, Z_FLOOR + LIP), "v", -8),
    ], notes=[Note("right", (XO, -Y1, Z_FLOOR + LIP), f"lips {LIP:g} high, full width, front and back",
                   side="above", along=-10)])]
    detail = ("front lip under the Ethernet plug", (0, -Y1, Z_FLOOR + 6), 22)
    return parts, sheets, Plane.YZ, "Solo10G desk bracket — cradle fit coupon", detail


SLICER = {"cradle": {"enable_support": "1"}}   # the back end frame's bars span the openings when standing on end

VARIANTS = ("cradle", "coupon")


def build(variant: str = "cradle") -> Model:
    if variant == "full":
        variant = "cradle"
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    parts, sheets, section, title, detail = (cradle_concept if variant == "cradle" else coupon_concept)()
    return Model(name="desk_bracket_solo10g", title=title, parts=parts, sheets=sheets, section=section,
                 checks=lambda r, p: checks(r, p, variant), slicer=SLICER.get(variant, {}), detail=detail)


# ---------------------------------------------------------------- checks

def checks(report, parts, variant):
    dev = parts["device"].shape
    bracket = union([p.shape for p in parts.values() if not p.reference])
    rj45 = parts["rj45"].shape
    mv = lambda s, x=0.0, y=0.0, z=0.0: s.moved(Location((x, y, z)))

    report.check("device: no interference", overlap(bracket, dev) < 1e-4, f"{overlap(bracket, dev):.4f} mm³")
    # a sharp-edged box the device's size, on the floor, centred or pushed against either wall
    sharp = Box(DEV_W, DEV_D, 10, align=(C, C, MIN)).moved(Location((0, 0, Z_FLOOR)))
    report.check("device sits flat on the floor bars (sharp edges)",
                 all(overlap(bracket, mv(sharp, x=s * CLR)) < 1e-4 for s in (-1, 0, 1)),
                 "square inner corners: no contact but the floor, centred or against a wall")
    report.check("device: supported", overlap(bracket, mv(dev, z=-0.5)) > 1, "lowering it 0.5 mm collides")
    for label, axis, want in (("sideways", 0, CLR), ("front/back", 1, CLR_Y)):
        plays = [play(bracket, dev, axis, s) for s in (-1, 1)]
        report.dim(f"play {label}, each way (measured)", min(plays), want, tol=0.03)
    report.check("device drops in from above (before mounting)", overlap(bracket, mv(dev, z=DEV_H + 20)) < 1e-4)
    report.check("Ethernet plug clear of the cradle", overlap(bracket, rj45) < 1e-3, f"{overlap(bracket, rj45):.4f} mm³")
    report.at_least("room between the front lip and the Ethernet plug (measured)",
                    play(bracket, rj45, 2, -1, hi=5), JACK_MARGIN)

    if variant == "coupon":
        report.dim("lips: lift to clear them (measured)", lift_to_clear(bracket, dev), LIP, tol=0.1)
        same = abs((make_cradle() & bracket).volume - bracket.volume) < 1e-3
        report.check("coupon is the cradle's own geometry", same, "coupon ⊂ cradle")
        return

    desk_ = parts["desk"].shape
    up = play(desk_, dev, 2, 1, hi=10)
    report.dim("air between the device and the desk (measured)", up, DESK_GAP, tol=0.03)
    # held front to back at every height it can reach: on the floor bars the lips stop it, lifted the top bars
    lifts = [up * i / 10 for i in range(11)]
    for way, sign in (("front", -1), ("back", 1)):
        slide = max(play(bracket, mv(dev, z=h), 1, sign, hi=5) for h in lifts)
        report.check(f"device held at the {way} at any lift up to the desk", slide < CLR_Y + 0.5,
                     f"it slides at most {slide:.2f} mm, lifted anywhere from 0 to {up:.1f} mm")
    below = bracket & Box(400, 400, 100, align=(C, C, MAX)).moved(Location((0, 0, Z_FRAME - 0.01)))
    report.dim("lips alone: lift to clear them (measured; the top bars take over)", lift_to_clear(below, dev), LIP, tol=0.1)
    tb = parts["thunderbolt"].shape
    report.check("Thunderbolt plug clear of the cradle", overlap(bracket, tb) < 1e-3, f"{overlap(bracket, tb):.4f} mm³")
    report.check("plugs pull straight out", overlap(bracket, mv(rj45, y=-50)) < 1e-3 and overlap(bracket, mv(tb, y=40)) < 1e-3)

    screws_ = parts["screws"].shape.solids()
    recess = [play(bracket, sc, 2, 1, hi=3) for sc in screws_]
    report.check(f"#6 screws seat in all {len(screws_)} countersinks",
                 all(overlap(bracket, sc) < 1e-3 for sc in screws_) and max(recess) < 0.6,
                 f"heads sit {min(recess):.2f}–{max(recess):.2f} mm below flush (head {SCREW_HEAD:g} mm, "
                 f"countersink {CSK_D:g} mm, {CSK_ANGLE:g}°)")
    into = max(sc.bounding_box().max.Z for sc in screws_)
    report.check("screws stay inside the desk", into < DESK_T,
                 f"{into:.1f} mm into the desk (measured); it must be thicker than that")
    # each end of the U is tied: a slice at the desk and one at the floor are each one piece, and a ring
    # (cut across the middle both ways, it falls into two pieces each way)
    for label, z in (("at the top", Z_TOP - 1.0), ("at the floor", Z_FLOOR - 1.0)):
        ring = bracket & Box(400, 400, 1.0, align=(C, C, MAX)).moved(Location((0, 0, z)))
        halves = [len((ring - Box(*size)).solids()) for size in ((1, 400, 400), (400, 1, 400))]
        report.check(f"one closed frame {label}", len(ring.solids()) == 1 and halves == [2, 2],
                     f"a 1 mm slice: {len(ring.solids())} piece(s); cut across x=0 and y=0: {halves[0]} and {halves[1]}")

    # the floor rails, mid-span: each one piece, at least RAIL_MIN_AREA in section
    mid = bracket & Box(400, 0.2, 100, align=(C, C, MAX)).moved(Location((0, 0, Z_FLOOR + 0.01)))
    rails = mid.solids()
    areas = [abs(r.volume) / 0.2 for r in rails]
    sizes = [f"{r.bounding_box().size.X:.1f} × {r.bounding_box().size.Z:.1f} mm, {a:.0f} mm²" for r, a in zip(rails, areas)]
    report.check("floor rails: section at mid-span", len(rails) == 2 and min(areas) >= RAIL_MIN_AREA,
                 "; ".join(sizes) + f" (minimum {RAIL_MIN_AREA:g}; the 4 × 4 rail that broke was ~15)")

    # the air pocket between the base plate and the desk: open at the desk along both sides, to the room (the
    # top bars close the ends). On each side, cross-sections of the way out (from the device's edge to the cradle's): the tightest one's free area
    def way_out(axis, side):
        width = DEV_D if axis == 0 else DEV_W
        x0, x1 = (DEV_W / 2, XF) if axis == 0 else (DEV_D / 2, Y1)
        free = []
        for i in range(9):
            c = side * (x0 + 0.3 + (x1 - x0 - 0.6) * i / 8)
            size = (0.2, width, DESK_GAP) if axis == 0 else (width, 0.2, DESK_GAP)
            at = (c, 0, -DESK_GAP / 2) if axis == 0 else (0, c, -DESK_GAP / 2)
            free.append(max(0.0, width * DESK_GAP - overlap(bracket, Box(*size).moved(Location(at))) / 0.2))
        return min(free), width * DESK_GAP
    vents = {name: way_out(axis, side) for name, axis, side in
             (("front", 1, -1), ("back", 1, 1), ("left", 0, -1), ("right", 0, 1))}
    report.check("air pocket over the device vents at the desk, out both sides",
                 min(vents[k][0] / vents[k][1] for k in ("left", "right")) > 0.4,
                 ", ".join(f"{k} {f:.0f} mm² ({100 * f / full:.0f} %)" for k, (f, full) in vents.items())
                 + " open, at the tightest section")

    # airflow: the fins (top, now facing down; left; right) and the end faces, measured as bracket shadow
    fins_down = face_coverage(dev, bracket, 2, -1)
    sides = [face_coverage(dev, bracket, 0, s) for s in (-1, 1)]
    report.check("top fins (facing down) covered", fins_down < 0.25, f"{100 * fins_down:.0f} %", warn_only=True)
    report.check("side fins covered", max(sides) < 0.25, f"{100 * sides[0]:.0f} % / {100 * sides[1]:.0f} %", warn_only=True)
    ends = [face_coverage(dev, bracket, 1, s) for s in (-1, 1)]
    report.check("end faces covered (by the lips)", True, f"front {100 * ends[0]:.0f} %, back {100 * ends[1]:.0f} %")
    report.check("base plate (towards the desk) covered", face_coverage(dev, bracket, 2, 1, reach=DESK_GAP - 0.1) < 0.005)

    bb = bracket.bounding_box()
    touching = bracket & Box(400, 400, 0.2, align=(C, C, MAX))
    report.check("hangs below the desk", True, f"{-bb.min.Z:.1f} mm")
    report.check("desk footprint", True, f"{bb.size.X:.0f} × {bb.size.Y:.0f} mm, {abs(touching.volume) / 0.2 / 100:.0f} cm² against it")
    report.check("screws", True, f"{len(screws_)}, {DEV_MASS * 9.81 / len(screws_):.1f} N each (the device's weight shared)")
