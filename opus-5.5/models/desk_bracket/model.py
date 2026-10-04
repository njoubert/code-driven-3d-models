"""Under-desk bracket for an OWC Express 4M2 Ultra: three concepts as variants
(upright, flat, drawer). See design.md.

Axes: X = left→right, Y = front→back (front = −Y; ports at +Y), Z = up.
The desk underside is z = 0; brackets and device hang below it.
"""

from __future__ import annotations

from build123d import (Align, Axis, Box, Cone, Cylinder, Location, Plane, Polygon, Rectangle, Rot,
                       Vector, chamfer, extrude, fillet)

from common.model import Dim, Model, Note, Part, Sheet

C, MIN, MAX = Align.CENTER, Align.MIN, Align.MAX

# ---- the device (published dimensions; measure to confirm)
DEV_W, DEV_H, DEV_D = 60.0, 123.0, 117.0
DEV_MASS = 0.9                 # kg
DEV_R = 3.0                    # body edge radius (assumed)
BORDER = 3.0                   # front/back edge border that may be covered (owner: "several mm")

# ---- fit
CLR = 0.6                      # per side, across the device
CLR_Y = 0.5                    # front/back, between device and lips
LIFT = 3.5                     # space above the device, to lift it over the front lip
FRONT_LIP = 2.5                # < BORDER, and < LIFT - 0.5 so the device can be lifted over it
BACK_STOP = 2.8                # ≤ BORDER
STOP_T = 2.5                   # lip / stop thickness along Y

# ---- straps (upright, flat)
T = 5.0                        # arm and floor thickness
TF = 5.0                       # flange thickness
FLANGE = 18.0                  # flange reach beyond the arm
SW = 14.0                      # strap width along Y: the arms sit on the solid edge columns, not the fins

# ---- drawer
TT, TFL = 3.5, 3.0             # tray wall, floor
RUN_W, RUN_T = 6.0, 4.0        # runner reach and thickness; its underside is a 45° slope (prints unsupported)
RUN_GAP = 1.5                  # runner top to desk: how far the cage can lift (detent)
SLOPE_GAP = 0.05               # runner slope to rail slope (the cage rests on the slopes)
RC = 0.5                       # runner tip to rail web clearance
LEDGE_T, WEB_T = 4.0, 4.0
DETENT_R, DETENT_H = 1.5, 0.7  # ridge on the rail's slope / notch in the runner, height normal to the slope
DETENT_Y = -(DEV_D / 2 + CLR_Y + STOP_T) + SW / 2   # in the front frame's runner
HANDLE_W, HANDLE_L = 36.0, 12.0

# ---- screws: 4 mm (#8) countersunk wood screws
SCREW_D, CSK_D = 4.5, 9.0
DESK_T = 18.0

PETG = "PETG"                  # recommended; the project files load the PLA preset, so switch filament

# ---- inverted: upside down, rubber feet pressed against the desk
FEET_H, FEET_W = 1.0, 8.0      # rubber strips on the device's bottom (assumed size)
FEET_INSET = 10.0              # strip centre from the side
PRELOAD = 0.5                  # how far the straps press the feet into the desk
RAMP = 1.5                     # lead-in chamfer on the front strap's floor

# ---- cradle: one part, upside down, feet against the desk, lips front and back
CRADLE_PRELOAD = 0.4           # feet pressed into the desk when the screws are tight (tune after a test)
CRADLE_LIP = 4.0               # lip height front and back
CRADLE_BORDER = 6.0            # solid border at the device's own top edge, front and back: ~9–10 mm in the
                               # owner's photos, so 6 mm is a safe allowance for the coverage check
POST = 12.0                    # solid end posts of the side walls (over the device's ~8 mm edge columns)
RAIL = 6.0                     # side-wall rails along the top and bottom between the posts

# ---- the fins proper, from the owner's side photo: solid edge columns ~8 mm at the front and
# back, a ~4 mm frame top and bottom. Fin coverage is measured inside these.
FIN_COLUMN, FIN_FRAME = 8.0, 4.0
BEAM = 12.0                    # floor strips left either side of the floor windows
SCREWS_PER_SIDE = 3


# ---------------------------------------------------------------- helpers

def prism(face, y0, y1):
    """Extrude a profile drawn in (x, z) from y = y0 to y = y1. The direction is explicit:
    a face's normal can flip after 2D booleans and fillets, and extrude() follows it."""
    at_y0 = Plane(origin=(0, y0, 0), x_dir=(1, 0, 0), z_dir=(0, -1, 0))   # local (u, v) = (x, z)
    return extrude(at_y0 * face, amount=y1 - y0, dir=(0, 1, 0))


def profile(outer_pts, holes=(), corners=()):
    """2D profile in (x, z): polygon minus rectangles (x0, z0, x1, z1), with rounded corners (x, z, r)."""
    face = Polygon(*outer_pts, align=None).face()
    for x0, z0, x1, z1 in holes:
        face = (face - Rectangle(x1 - x0, z1 - z0, align=(MIN, MIN)).moved(Location((x0, z0)))).face()
    for x, z, r in corners:
        v = min(face.vertices(), key=lambda v: (v.X - x) ** 2 + (v.Y - z) ** 2)
        face = face.fillet_2d(r, [v])
    return face


def countersunk(x, y, z_bottom, length):
    """Screw hole up into the desk, countersunk from the underside at z_bottom."""
    h = (CSK_D - SCREW_D) / 2
    return (Cylinder(SCREW_D / 2, length + 2, align=(C, C, MIN)).moved(Location((x, y, z_bottom - 1)))
            + Cone(CSK_D / 2 + 0.1, SCREW_D / 2, h + 0.1, align=(C, C, MIN)).moved(Location((x, y, z_bottom - 0.1))))


def device_box(sx, sy, sz):
    box = Box(sx, sy, sz, align=(C, C, MAX)).moved(Location((0, 0, -LIFT)))
    return fillet(box.edges(), DEV_R)


def desk(span_x, span_y):
    return Box(span_x, span_y, DESK_T, align=(C, C, MIN))


# ---------------------------------------------------------------- straps

def strap(iw, ih, y0, y1, front_lip=0.0, back_stop=0.0):
    """U-strap: flanges on the desk, arms down, floor whose top is ih below the desk."""
    xi, xo, xf, zb = iw / 2, iw / 2 + T, iw / 2 + T + FLANGE, -(ih + T)
    prof = profile(
        [(-xf, 0), (xf, 0), (xf, -TF), (xo, -TF), (xo, zb), (-xo, zb), (-xo, -TF), (-xf, -TF)],
        holes=[(-xi, -ih, xi, 1)],
        corners=[(s * xi, -ih, 2.5) for s in (-1, 1)] + [(s * xo, zb, 6) for s in (-1, 1)]
                + [(s * xo, -TF, 5) for s in (-1, 1)] + [(s * xf, -TF, 2) for s in (-1, 1)])
    body = prism(prof, y0, y1)
    if front_lip:
        body += Box(iw - 6, STOP_T, front_lip, align=(C, MIN, MIN)).moved(Location((0, y0, -ih)))
    if back_stop:
        body += Box(iw - 6, STOP_T, back_stop, align=(C, MAX, MIN)).moved(Location((0, y1, -ih)))
    for s in (-1, 1):
        body -= countersunk(s * (xo + FLANGE / 2 + 1), (y0 + y1) / 2, -TF, TF)
    return body


def strap_concept(variant):
    upright = variant == "upright"
    sx, sz = (DEV_W, DEV_H) if upright else (DEV_H, DEV_W)
    iw, ih = sx + 2 * CLR, sz + LIFT
    yf = -(DEV_D / 2 + CLR_Y + STOP_T)
    front = strap(iw, ih, yf, yf + SW, front_lip=FRONT_LIP)
    back = strap(iw, ih, -yf - SW, -yf, back_stop=BACK_STOP)
    device = device_box(sx, DEV_D, sz)
    stand = Location((0, 0, 0), (90, 0, 0))                  # print standing on its front face
    parts = [
        Part("strap_front", front, color="#e07a3f", print_pose=stand),
        Part("strap_back", back, color="#e07a3f", print_pose=stand),
        Part("device", device, color="#5b6068", reference=True, explode=(0, 0, -25)),
        Part("desk", desk(iw + 2 * (T + FLANGE) + 40, DEV_D + 60), color="#c8a978", reference=True, opacity=0.25),
    ]
    name = "upright" if upright else "on its side"
    sheets = [Sheet("strap_front", material=PETG, dims=[
        Dim("front", (-iw / 2, yf, -ih), (iw / 2, yf, -ih), "h", -16),
        Dim("front", (iw / 2, yf, -ih), (iw / 2, yf, 0), "v", 8),
    ], notes=[Note("front", (0, yf, -ih + FRONT_LIP), f"front lip {FRONT_LIP:g} high", side="below", along=10)]),
        Sheet("strap_back", material=PETG)]
    return parts, sheets, Plane.XZ.offset(-(yf + SW / 2)), f"Desk bracket — sling, {name}"


def inverted_concept():
    """Upside down: the straps press the device's rubber feet against the desk. Held by the
    compressed rubber's friction; no lips, so nothing covers the front or back."""
    iw = DEV_W + 2 * CLR
    body_top = -(FEET_H - PRELOAD)                 # feet stand FEET_H proud and are pressed PRELOAD into the desk
    ih = DEV_H - body_top                          # floor top = device body's lowest point
    y0, y1 = -DEV_D / 2, DEV_D / 2
    front = strap(iw, ih, y0, y0 + SW)
    lead_in = front.edges().filter_by(Axis.X).filter_by(
        lambda e: abs(e.center().Y - y0) < 0.01 and abs(e.center().Z + ih) < 0.01)
    front = chamfer(lead_in, RAMP)                 # ramp on the floor's front edge: push the device in
    back = strap(iw, ih, y1 - SW, y1)
    device = fillet(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MAX)).moved(Location((0, 0, body_top))).edges(), DEV_R)
    for sx in (-1, 1):                             # rubber strips, now on top
        device += Box(FEET_W, DEV_D - 10, FEET_H, align=(C, C, MIN)).moved(
            Location((sx * (DEV_W / 2 - FEET_INSET), 0, body_top)))
    stand = Location((0, 0, 0), (90, 0, 0))
    parts = [
        Part("strap_front", front, color="#e07a3f", print_pose=stand),
        Part("strap_back", back, color="#e07a3f", print_pose=stand),
        Part("device", device, color="#5b6068", reference=True, explode=(0, 0, -25)),
        Part("desk", desk(iw + 2 * (T + FLANGE) + 40, DEV_D + 60), color="#c8a978", reference=True, opacity=0.25),
    ]
    sheets = [Sheet("strap_front", material=PETG, dims=[
        Dim("front", (-iw / 2, y0, -ih), (iw / 2, y0, -ih), "h", -16),
        Dim("front", (iw / 2, y0, -ih), (iw / 2, y0, 0), "v", 8),
    ], notes=[Note("right", (0, y0, -ih), f"{RAMP:g} mm lead-in ramp", side="below", along=0)]),
        Sheet("strap_back", material=PETG)]
    return parts, sheets, Plane.XZ.offset(-(y0 + SW / 2)), "Desk bracket — inverted, feet against the desk"


def house(u0, u1, v0, v1):
    """Window from u0 to u1, flat at u0 and with a 45° point at u1: self-supporting when printed
    with u pointing up (the flat end is the bottom of the hole, the point is its roof)."""
    h = (v1 - v0) / 2
    return Polygon((u0, v0), (u1 - h, v0), (u1, (v0 + v1) / 2), (u1 - h, v1), (u0, v1), align=None)


def cradle_concept():
    """One part: the U-profile runs the full depth with continuous flanges, so both ends and all
    screw holes are fixed relative to each other. The device sits upside down, rubber feet pressed
    against the desk, held front and back by low lips. Side and floor windows keep the fins open.
    Install: drop the device in, then screw the cradle up under the desk."""
    iw = DEV_W + 2 * CLR
    body_top = -(FEET_H - CRADLE_PRELOAD)
    ih = DEV_H - body_top                          # floor top = device body's lowest point
    xi, xo, xf = iw / 2, iw / 2 + T, iw / 2 + T + FLANGE
    y0, y1 = -(DEV_D / 2 + CLR_Y + STOP_T), DEV_D / 2 + CLR_Y + STOP_T

    cradle = strap(iw, ih, y0, y1)                 # full-length U with both flanges (holes added below)
    # side walls: one open rectangle each, between the end posts and the thin top/bottom rails.
    # Printed standing on its front end, the back post spans the opening: supports hold it up.
    ya, yb, za, zb = y0 + POST, y1 - POST, -(TF + RAIL), -ih + RAIL
    cradle -= Box(2 * (xo + 1), yb - ya, za - zb, align=(C, MIN, MIN)).moved(Location((0, ya, zb)))
    # floor window, leaving a strip each side under the device's flat top plate. Its 45° point
    # (at the back) is its own roof when printed standing up, so it needs no support.
    wx = iw / 2 - BEAM
    floor = Plane(origin=(0, 0, -(ih + T) - 1), x_dir=(0, 1, 0), z_dir=(0, 0, 1))
    cradle -= extrude(floor * house(y0 + POST, y1 - POST, -wx, wx), amount=T + 2, dir=(0, 0, 1))
    # lips front and back, on the floor
    cradle += Box(iw - 6, STOP_T, CRADLE_LIP, align=(C, MIN, MIN)).moved(Location((0, y0, -ih)))
    cradle += Box(iw - 6, STOP_T, CRADLE_LIP, align=(C, MAX, MIN)).moved(Location((0, y1, -ih)))
    # replace strap()'s single centred screw per side with three along each flange
    for sx in (-1, 1):
        for y in (y0 + 14, 0.0, y1 - 14):
            cradle -= countersunk(sx * (xo + FLANGE / 2 + 1), y, -TF, TF)

    device = fillet(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MAX)).moved(Location((0, 0, body_top))).edges(), DEV_R)
    for sx in (-1, 1):                             # rubber strips, now on top against the desk
        device += Box(FEET_W, DEV_D - 10, FEET_H, align=(C, C, MIN)).moved(
            Location((sx * (DEV_W / 2 - FEET_INSET), 0, body_top)))
    stand = Location((0, 0, 0), (90, 0, 0))        # print standing on its front end
    parts = [
        Part("cradle", cradle, color="#e07a3f", print_pose=stand),
        Part("device", device, color="#5b6068", reference=True, explode=(0, 0, -40)),
        Part("desk", desk(2 * xf + 40, DEV_D + 60), color="#c8a978", reference=True, opacity=0.25),
    ]
    sheets = [Sheet("cradle", material=PETG, dims=[
        Dim("front", (-iw / 2, y0, -ih), (iw / 2, y0, -ih), "h", -16),
        Dim("front", (xi, y0, -ih), (xi, y0, 0), "v", 8),
        Dim("right", (xo, y0, -ih), (xo, y1, -ih), "h", -16),
    ], notes=[Note("right", (xo, y1 - STOP_T / 2, -ih + CRADLE_LIP), f"lip {CRADLE_LIP:g} high, front and back",
                   side="above", along=-10),Note("top", (xo + FLANGE / 2 + 1, 0, 0), f"{2 * SCREWS_PER_SIDE}× countersunk, 4 mm wood screws",
                   side="right", along=0)])]
    return parts, sheets, Plane.YZ, "Desk bracket — cradle (one part, upside down, lipped)"


# ---------------------------------------------------------------- drawer

def drawer_concept():
    """Upright cage on desk rails: front and back U-frames joined by top runners and floor beams.
    The device drops into the cage from above; the cage slides into the rails like a drawer."""
    iw = DEV_W + 2 * CLR
    zt = -RUN_GAP                                   # runner top

    def detent(s, r):
        """Cylinder lying along the 45° slope, standing DETENT_H proud of it, at DETENT_Y."""
        xm = xo + RUN_W / 2 + 0.5                                     # mid-slope
        zm = zt - RUN_T - (xr - xm) - SLOPE_GAP                       # on the rail's slope surface
        n = Vector(-0.70710678, 0, 0.70710678)                        # slope normal, up and inward
        c = Vector(xm, DETENT_Y, zm) + n * (DETENT_H - DETENT_R)
        cyl = Cylinder(r, RUN_W - 1.5).moved(Plane(origin=c, z_dir=(1, 0, 1)).location)
        return cyl if s > 0 else cyl.mirror(Plane.YZ)
    dev_top = zt - 0.5
    zf = dev_top - DEV_H                            # floor top = device bottom
    zb = zf - T
    xi, xo, xr = iw / 2, iw / 2 + T, iw / 2 + T + RUN_W
    y0, y1 = -(DEV_D / 2 + CLR_Y + STOP_T), DEV_D / 2 + CLR_Y + STOP_T

    zs = zt - RUN_T - RUN_W                        # where the runner's 45° underside meets the arm
    frame = profile(
        [(-xr, zt), (xr, zt), (xr, zt - RUN_T), (xo, zs), (xo, zb), (-xo, zb), (-xo, zs), (-xr, zt - RUN_T)],
        holes=[(-xi, zf, xi, zt + 1)],
        corners=[(s * xi, zf, 2.5) for s in (-1, 1)] + [(s * xo, zb, 5) for s in (-1, 1)])
    cage = prism(frame, y0, y0 + SW) + prism(frame, y1 - SW, y1)
    for s in (-1, 1):
        a = MIN if s > 0 else MAX
        cage += Box(12, y1 - y0, T, align=(a, MIN, MIN)).moved(Location((s * (xi - 12), y0, zb)))       # floor beam
        cage -= detent(s, DETENT_R + 0.15)                                                              # notch
    cage += Box(iw - 6, STOP_T, BACK_STOP, align=(C, MIN, MIN)).moved(Location((0, y0, zf)))          # front tab
    cage += Box(iw - 6, STOP_T, BACK_STOP, align=(C, MAX, MIN)).moved(Location((0, y1, zf)))          # back tab
    handle = Box(HANDLE_W, HANDLE_L, T, align=(C, MAX, MIN)).moved(Location((0, y0, zb)))
    handle -= Box(HANDLE_W - 12, HANDLE_L - 5, T + 2).moved(Location((0, y0 - HANDLE_L / 2 - 1, zb + T / 2)))
    cage += handle

    zl = zs - LEDGE_T
    xin = xo + 1.0                                 # the rail's slope stops short of the cage's arm
    def rail(s):
        xw0, xw1 = xr + RC, xr + RC + WEB_T
        g = SLOPE_GAP
        pts = [(xw1 + FLANGE, 0), (xw0, 0), (xw0, zt - RUN_T - g), (xr, zt - RUN_T - g),
               (xin, zt - RUN_T - (xr - xin) - g), (xin, zl), (xw1, zl), (xw1, -TF), (xw1 + FLANGE, -TF)]
        r = prism(profile(pts, corners=[(xw1, -TF, 2.0), (xw1, zl, 1.5), (xin, zl, 1.0)]), y0, y1 + 4)
        r += Box(xw0 - xin, 4, zt - zl, align=(MIN, MIN, MIN)).moved(Location((xin, y1, zl)))   # back stop
        r += detent(1, DETENT_R)                                                                # ridge
        for y in (y0 + 20, y1 - 20):
            r -= countersunk(xw1 + FLANGE / 2, y, -TF, TF)
        return r if s > 0 else r.mirror(Plane.YZ)

    device = fillet(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MAX)).moved(Location((0, 0, dev_top))).edges(), DEV_R)
    end_on = Location((0, 0, 0), (-90, 0, 0))      # rails: print standing on the back end
    parts = [
        Part("cage", cage, color="#3f8fe0", explode=(0, -80, 0)),   # prints as used: floor beams on the bed
        Part("rail_left", rail(-1), color="#e07a3f", print_pose=end_on),
        Part("rail_right", rail(1), color="#e07a3f", print_pose=end_on),
        Part("device", device, color="#5b6068", reference=True, explode=(0, -80, 0)),
        Part("desk", desk(2 * (xr + RC + WEB_T + FLANGE) + 40, DEV_D + 70), color="#c8a978", reference=True, opacity=0.25),
    ]
    sheets = [Sheet("cage", material=PETG, notes=[Note("front", (0, y0, zb), "pull handle", side="below", along=20)]),
              Sheet("rail_right", material=PETG)]
    return parts, sheets, Plane.XZ.offset(-DETENT_Y), "Desk bracket — drawer (upright cage)"


SLICER = {"cradle": {"enable_support": "1"}}   # tree supports under the back posts, in the side openings


# ---------------------------------------------------------------- model

VARIANTS = ("cradle", "upright", "inverted", "flat", "drawer")


def build(variant: str = "cradle") -> Model:
    if variant == "full":
        variant = "cradle"
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    concept = {"drawer": drawer_concept, "inverted": inverted_concept, "cradle": cradle_concept}.get(
        variant, lambda: strap_concept(variant))
    parts, sheets, section, title = concept()
    return Model(name="desk_bracket", title=title, parts=parts, sheets=sheets, section=section,
                 checks=lambda r, p: checks(r, p, variant), slicer=SLICER.get(variant, {}))


# ---------------------------------------------------------------- checks

def _overlap(a, b) -> float:
    return abs((a & b).volume) if a is not None else 0.0


def _union(shapes):
    u = shapes[0]
    for s in shapes[1:]:
        u = u + s
    return u


def face_coverage(device, brackets, axis: int, side: int, inset: float = 0.0, reach: float = 8.0,
                  insets: dict | None = None) -> float:
    """Fraction of a device face shadowed by bracket material within `reach` mm of it,
    ignoring an `inset` border (or per-axis `insets`, {axis index: mm}). Projected area
    from a slab in front of the face."""
    b = device.bounding_box()
    lo, hi = [b.min.X, b.min.Y, b.min.Z], [b.max.X, b.max.Y, b.max.Z]
    a, o = axis, [i for i in range(3) if i != axis]
    size, centre = [0.0] * 3, [0.0] * 3
    for i in o:
        size[i] = hi[i] - lo[i] - 2 * (insets.get(i, inset) if insets else inset)
        centre[i] = (hi[i] + lo[i]) / 2
    size[a] = reach
    centre[a] = (hi[a] + reach / 2 + 0.01) if side > 0 else (lo[a] - reach / 2 - 0.01)
    slab = Box(*size).moved(Location(tuple(centre)))
    hit = slab & brackets
    if not hit or abs(hit.volume) < 1e-6:
        return 0.0
    n = [0.0, 0.0, 0.0]
    n[a] = 1.0
    proj = sum(f.area * abs(f.normal_at().dot(Vector(*n))) for f in hit.faces()) / 2
    return min(proj / (size[o[0]] * size[o[1]]), 1.0)


def checks(report, parts, variant):
    dev = parts["device"].shape
    printed = [p.shape for name, p in parts.items() if not p.reference]
    brackets = _union(printed)
    db = dev.bounding_box()
    mv = lambda s, x=0.0, y=0.0, z=0.0: s.moved(Location((x, y, z)))

    report.check("device: no interference", _overlap(brackets, dev) < 1e-4, f"{_overlap(brackets, dev):.4f} mm³")

    if variant == "drawer":
        tray = parts["cage"].shape
        rails = parts["rail_left"].shape + parts["rail_right"].shape
        unit = tray + dev
        report.check("tray: rests on the rails", _overlap(rails, mv(tray, z=-0.5)) > 1, "lowering it 0.5 mm collides")
        report.check("tray: back stop", _overlap(rails, mv(tray, y=1.0)) > 0.1, "pushing it 1 mm back collides")
        report.check("tray: detent holds it in", _overlap(rails, mv(tray, y=-3.0)) > 0.01, "pulling it 3 mm forward collides")
        lift = DETENT_H * 2 ** 0.5 + 0.15           # ridge stands DETENT_H proud of a 45° slope
        report.check("tray: pulls out after lifting over the detent",
                     _overlap(rails, mv(tray, y=-(DEV_D + 40), z=lift)) < 1e-4
                     and lift < RUN_GAP, f"lift {lift:.2f} mm of {RUN_GAP:g} mm available")
        report.check("device lifts out of the tray", _overlap(tray, mv(dev, z=db.size.Z + 5)) < 1e-4)
        report.check("device held in the tray", _overlap(tray, mv(dev, y=-1.5)) > 0.01 and _overlap(tray, mv(dev, x=1.5)) > 0.01,
                     "sliding it 1.5 mm forward or sideways collides")
    elif variant == "cradle":
        desk_ = parts["desk"].shape
        feet_area = 2 * FEET_W * (DEV_D - 10)
        report.dim("rubber feet pressed into the desk", _overlap(desk_, dev) / feet_area, CRADLE_PRELOAD, tol=0.05)
        report.check("device: supported", _overlap(brackets, mv(dev, z=-0.5)) > 1, "lowering it 0.5 mm collides")
        report.check("device: lips hold it front and back",
                     _overlap(brackets, mv(dev, y=-(CLR_Y + 1))) > 0.01 and _overlap(brackets, mv(dev, y=CLR_Y + 1)) > 0.01)
        report.check("device: held sideways", _overlap(brackets, mv(dev, x=1.5)) > 0.01)
        report.check("device drops in from above (before mounting)",
                     _overlap(brackets, mv(dev, z=DEV_H + 10)) < 1e-4)
    elif variant == "inverted":
        report.check("device: supported", _overlap(brackets, mv(dev, z=-0.5)) > 1, "lowering it 0.5 mm collides")
        desk_ = parts["desk"].shape
        feet_area = 2 * FEET_W * (DEV_D - 10)
        squeeze = _overlap(desk_, dev) / feet_area
        report.dim("rubber feet pressed into the desk", squeeze, PRELOAD, tol=0.05)
        report.check("device: slides in and out (friction hold, no lips)",
                     _overlap(brackets, mv(dev, y=-(DEV_D + 40))) < 1e-4)
    else:
        report.check("device: supported", _overlap(brackets, mv(dev, z=-0.5)) > 1, "lowering it 0.5 mm collides")
        report.check("device: back stop", _overlap(brackets, mv(dev, y=CLR_Y + 1.0)) > 0.01)
        report.check("device: front lip holds it", _overlap(brackets, mv(dev, y=-(CLR_Y + 1.0))) > 0.01)
        lift = FRONT_LIP + 0.3
        free = _overlap(brackets, mv(dev, y=-(DEV_D + 40), z=lift)) < 1e-4
        report.check("device: slides out after lifting over the lip", free and db.max.Z + lift <= 0,
                     f"lift {lift:.1f} mm; space above device {-db.max.Z:.1f} mm")

    # airflow: front (intake) and back (exhaust + ports) open inside the border; fin coverage
    border = CRADLE_BORDER if variant == "cradle" else BORDER
    for name, side in (("front", -1), ("back", +1)):
        cov = face_coverage(dev, brackets, 1, side, border)
        report.check(f"{name} face open inside the {border:g} mm border", cov < 0.005, f"{100 * cov:.1f} % covered")
    fin_axis = 2 if variant == "flat" else 0
    other = [i for i in range(3) if i not in (fin_axis, 1)][0]          # the fins' "height" axis
    fin_area = {1: FIN_COLUMN, other: FIN_FRAME}                         # inside the edge columns and frame
    fins = [face_coverage(dev, brackets, fin_axis, s, insets=fin_area) for s in (-1, 1)]
    report.check("fins covered", max(fins) < 0.4,
                 f"{100 * fins[0]:.0f} % / {100 * fins[1]:.0f} % of the fin area (within 8 mm of it)", warn_only=True)

    # comparison numbers
    allb = brackets.bounding_box()
    drop = -min(allb.min.Z, db.min.Z)
    screws = 2 * SCREWS_PER_SIDE if variant == "cradle" else 4
    report.check("hangs below the desk", True, f"{drop:.0f} mm")
    report.check("desk footprint", True, f"{allb.size.X:.0f} × {allb.size.Y:.0f} mm")
    report.check("screws", True, f"{screws}, {DEV_MASS * 9.81 / screws:.1f} N each (the device's weight shared)")
