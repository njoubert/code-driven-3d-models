"""Under-desk bracket for an OWC Express 4M2 Ultra. The chosen design is `cradle`; `coupon` is its
fit test; the earlier concepts are kept as variants (upright, inverted, flat, drawer). See design.md.

Axes: X = left→right, Y = front→back (front = −Y; ports at +Y), Z = up.
The desk underside is z = 0; brackets and device hang below it.
"""

from __future__ import annotations

import math

from build123d import (Align, Axis, Box, Cone, Cylinder, Location, Plane, Polygon, Rectangle,
                       Rot, Vector, chamfer, extrude, fillet)

from common.model import Dim, Model, Note, Part, Sheet

C, MIN, MAX = Align.CENTER, Align.MIN, Align.MAX

# ---- the device. Width and depth published (the coupon fit as modelled); height measured with
# calipers (body without the rubber feet)
DEV_W, DEV_H, DEV_D = 60.0, 122.12, 117.0
DEV_MASS = 0.9                 # kg
DEV_R = 3.0                    # radius of the 4 rounded corners where the front and back panels meet the
                               # side panels (size assumed from the photos). All other edges are sharp 90°
                               # machined aluminium (owner; cradle v1 rode up on its rounded inner corners)
BORDER = 3.0                   # front/back edge border that may be covered (owner: "several mm")

# ---- fit
CLR = 0.2                      # per side, across the device. Was 0.6: cradle v1 had ~1 mm of sideways slop
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

# ---- screws: #6 × 5/8" flat-head construction screws (owner): 3.5 mm shank, ~6.9 mm head, 82° countersink
SCREW_SIZE, SCREW_L, SCREW_HEAD = 3.5, 15.9, 6.9
SCREW_D = 4.0                  # clearance hole (printed holes come out a little small)
CSK_D, CSK_ANGLE = 7.4, 82.0   # countersink: a little over the head, so it seats flush
DESK_T = 18.0

PETG = "PETG"                  # recommended; the project files load the PLA preset, so switch filament

# ---- inverted: upside down, rubber feet pressed against the desk
FEET_H, FEET_W = 1.24, 5.7     # rubber strips on the device's bottom, measured: 1.24 tall (123.36 with, 122.12
                               # without), 5.7 wide
FEET_INSET = 2.0 + FEET_W / 2  # strip centre from the side: measured 2 mm in from the edge
PRELOAD = 0.5                  # how far the straps press the feet into the desk
RAMP = 1.5                     # lead-in chamfer on the front strap's floor

# ---- cradle: one part, device upside down on a foam pad, hanging free of the desk, lips front and back
CRADLE_CLR_Y = 0.2             # front/back, device to lips. Coupon v1 (0.5 each end): 7 sheets of HP
                               # Premium32 (5.2 mil, 0.132 mm) fit end to end, not 8 -> 0.92-1.06 mm slack,
                               # as modelled (so DEV_D 117 is right), but too loose. Expect 3 sheets, not 4
FOAM_GAP = 2.0                 # foam pad under the device (owner), as it sits under the device's weight
DESK_GAP = 3.0                 # air between the feet and the desk (owner): the device hangs free in the cradle,
                               # touching only foam, so less fan vibration reaches the desk
FOAM_W = 9.0                   # reference foam strips, one on each floor strip beside the window
CRADLE_LIP = 6.0               # how far the lips reach up the device's end faces (they stand FOAM_GAP taller):
                               # up to CRADLE_BORDER, so the faces stay open
CRADLE_BORDER = 6.0            # solid border at the device's own top edge, front and back: ~9–10 mm in the
                               # owner's photos, so 6 mm is a safe allowance for the coverage check
FRONT_SOLID_TOP, FRONT_SOLID_FEET = 9.38, 23.0   # the front panel is solid (no grille holes) this far from the
                               # top plate and from the feet-side plate (measured, owner); the grille is between
POST = 12.0                    # solid end posts of the side walls (over the device's ~8 mm edge columns)
RAIL = 6.0                     # side-wall rails along the top and bottom between the posts

# ---- the fins proper, from the owner's side photo: solid edge columns ~8 mm at the front and
# back, a ~4 mm frame top and bottom. Fin coverage is measured inside these.
FIN_COLUMN, FIN_FRAME = 8.0, 4.0
BEAM = 12.0                    # floor strips left either side of the floor windows

# ---- cable tail: a plate behind the device, flat against the desk, with zip-tie anchors underneath.
# The owner loops each cable before tying it, so the anchors needn't be far enough back for a gentle
# bend: they sit just behind the opening.
# Ports: heights measured (owner) from the body's bottom plate (the feet side, not counting the feet):
# power centre 22.7, lower Thunderbolt centre 38.0, upper Thunderbolt centre 54.5; 19 to the bottom of
# the lowest, 60 to the top of the highest. Their x and the plugs' sizes are from the back photo
# (**assumed**). Given as mounted upside down: x as seen there, "depth" below its top, which is the height
# above the feet-side plate.
PORTS_SPAN = (19.0, 60.0)
PORT_UP = {"power": 22.7, "thunderbolt": 38.0, "thunderbolt 2": 54.5}
#        name           x      depth (height above the feet-side plate)   plug (w, h)   plug length   cable radius
PLUGS = (("thunderbolt", -8.5, PORT_UP["thunderbolt"], (12.0, 10.0), 28.0, 2.5),   # lower port, OWC's screw-lock
         ("power",       -13.0, PORT_UP["power"], (9.0, 9.0), 25.0, 2.0))   # the upper Thunderbolt port is unused
EXHAUST = ((0.0, 8.0), (30.0, 81.0))   # exhaust slots: x range, depth range below the device's top (assumed)
TAIL_T = TF                    # plate thickness: flush with the flanges
TAIL_RIB = 7.0                 # the side walls continue this far below the plate along the tail
ANCHOR_X = (-20.0, 0.0, 20.0)  # 20 mm apart (12.5 mm between anchors: room for fingers and a tie), between the ribs
ANCHOR_W, ANCHOR_H = 7.5, 4.2  # each anchor: a block under the plate with a tunnel for the tie
TIE_W, TIE_T = 4.8, 1.3        # standard 4.8 mm zip ties
TUNNEL_W, TUNNEL_H = 5.5, 2.2
CABLE_D = (4.0, 5.3)           # cable diameters the anchors' cradles take (owner)
SADDLE_R = CABLE_D[1] / 2 + 0.1   # each anchor's underside has a round groove the cable sits in, sized for the
SADDLE_D = 1.6                 # thickest cable; it's SADDLE_D deep, so its sides come only partway around the
                               # cable (not past its widest point): any cable in the range seats, none snaps in

# ---- sidearm: the cradle with the device right side up and, instead of the tail, a tab off one side
# wall's back post, level with the ports, carrying the cable anchors: only the flanges touch the desk
# The front cross-bar matches the bottom lip plus floor (owner: symmetric from the front) without
# reaching the grille: the cradle is made taller instead, with more air above the device.
BAR_CLEAR = 0.9                # the cross-bar stops this far above the grille (room for the foam squeezing more)
SIDEARM_GAP = (T + FOAM_GAP + FEET_H + CRADLE_LIP) - (FRONT_SOLID_TOP - BAR_CLEAR)   # air above the device
BACK_LIP = SIDEARM_GAP + 1.75  # the back lip's reach up the device: it can now lift SIDEARM_GAP, and at the back
                               # no cross-bar stops it (the lowest port is 19 mm up)
ARM_L = 63.0                   # how far the tab reaches behind the cradle (room behind the plugs for the loops;
                               # sidearm v1 printed at 45, owner: ~40 % longer)
ARM_POST = 14.0                # the anchors are centred this far in from the tab's end
ARM_ANCHOR_UP = (21.0, 40.0, 59.0)   # anchor heights above the device's bottom: spread over PORTS_SPAN
TAB_MARGIN = 4.0               # the tab reaches this far above the top anchor's tie and below the bottom one's
TAB_R = 6.0                    # the tab's back corners are rounded

# ---- coupon: the cradle's base only, to test the fit before the full print
COUPON_FLOOR = 1.6             # floor kept under the device (the cradle's is T; thickness doesn't affect fit)
COUPON_WALL = 10.0             # wall kept above the floor top: the rails, and the posts' lower ends
COUPON_DEVICE = 25.0           # how much of the device the views show


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


def device_body(box, height_axis=Axis.Z):
    """The device from its bounding box: only the corners between the front/back and side panels
    (the edges along its height) are rounded; every other edge is sharp."""
    return fillet(box.edges().filter_by(height_axis), DEV_R)


def device_box(sx, sy, sz, height_axis=Axis.Z):
    return device_body(Box(sx, sy, sz, align=(C, C, MAX)).moved(Location((0, 0, -LIFT))), height_axis)


def desk(span_x, span_y):
    return Box(span_x, span_y, DESK_T, align=(C, C, MIN))


# ---------------------------------------------------------------- straps

def strap(iw, ih, y0, y1, front_lip=0.0, back_stop=0.0, screws=True):
    """U-strap: flanges on the desk, arms down, floor whose top is ih below the desk."""
    xi, xo, xf, zb = iw / 2, iw / 2 + T, iw / 2 + T + FLANGE, -(ih + T)
    prof = profile(
        [(-xf, 0), (xf, 0), (xf, -TF), (xo, -TF), (xo, zb), (-xo, zb), (-xo, -TF), (-xf, -TF)],
        holes=[(-xi, -ih, xi, 1)],
        corners=[(s * xo, zb, 6) for s in (-1, 1)]     # inner floor-to-wall corners stay square: the device's
                                                         # edges are sharp (cradle v1 rode up on 2.5 mm fillets)
                + [(s * xo, -TF, 5) for s in (-1, 1)] + [(s * xf, -TF, 2) for s in (-1, 1)])
    body = prism(prof, y0, y1)
    if front_lip:
        body += Box(iw - 6, STOP_T, front_lip, align=(C, MIN, MIN)).moved(Location((0, y0, -ih)))
    if back_stop:
        body += Box(iw - 6, STOP_T, back_stop, align=(C, MAX, MIN)).moved(Location((0, y1, -ih)))
    for s in (-1, 1) if screws else ():
        body -= countersunk(s * (xo + FLANGE / 2 + 1), (y0 + y1) / 2, -TF, TF)
    return body


def strap_concept(variant):
    upright = variant == "upright"
    sx, sz = (DEV_W, DEV_H) if upright else (DEV_H, DEV_W)
    iw, ih = sx + 2 * CLR, sz + LIFT
    yf = -(DEV_D / 2 + CLR_Y + STOP_T)
    front = strap(iw, ih, yf, yf + SW, front_lip=FRONT_LIP)
    back = strap(iw, ih, -yf - SW, -yf, back_stop=BACK_STOP)
    device = device_box(sx, DEV_D, sz, Axis.Z if upright else Axis.X)
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
    ramp = Polygon((y0 - 0.01, -ih + 0.01), (y0 + RAMP, -ih + 0.01), (y0 - 0.01, -ih - RAMP), align=None)
    side = Plane(origin=(-iw / 2, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))   # local (u, v) = (y, z)
    front -= extrude(side * ramp, amount=iw, dir=(1, 0, 0))   # ramp on the floor's front edge: push the device in
    back = strap(iw, ih, y1 - SW, y1)
    device = device_body(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MAX)).moved(Location((0, 0, body_top))))
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


def cradle_frame(right_side_up=False):
    """The cradle's key coordinates: inner width, floor top depth below the desk, wall x's, ends. Right side
    up (sidearm) there is SIDEARM_GAP of air above the device instead of DESK_GAP."""
    iw = DEV_W + 2 * CLR
    gap = SIDEARM_GAP if right_side_up else DESK_GAP
    body_top = -(FEET_H + gap)                     # the device's (upside-down) top: feet `gap` below the desk
    ih = DEV_H - body_top + FOAM_GAP               # floor top: FOAM_GAP below the device
    xi, xo, xf = iw / 2, iw / 2 + T, iw / 2 + T + FLANGE
    y0, y1 = -(DEV_D / 2 + CRADLE_CLR_Y + STOP_T), DEV_D / 2 + CRADLE_CLR_Y + STOP_T
    return iw, body_top, ih, xi, xo, xf, y0, y1


def tail_frame():
    """The cable tail, front to back: the opening behind the device (its 45° sides meet in a point
    at y1 + xi), the row of anchors just behind that point, then the plate's end."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame()
    a = TUNNEL_W / 2 + 2                           # half the anchor's length along Y, at its bottom
    point = y1 + xi
    tie_y = point + a + ANCHOR_H + SADDLE_D + 1    # the anchors' 45° fronts start behind the opening's point
    y_end = tie_y + a + 8
    return tie_y, a, y_end, point


def arm_frame():
    """The side arm: its end (y_end), the y of its anchors (centred on its end post), and the device's
    bottom (right side up: on its feet, on the foam), which the port and anchor heights are measured from."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(True)
    y_end = y1 + ARM_L
    return y_end, y_end - ARM_POST / 2, -ih + FOAM_GAP + FEET_H


def three_per_side(front, back):
    """Front, back, and one midway between them: the plastic between screws spans half as far."""
    return (front, (front + back) / 2, back)


def cradle_screws(style="tail"):
    """(x, y) of the cradle's 6 screws, three along each side. ~1 kg hangs on them; one #6 screw in
    11 mm of wood holds well over 100 N. "tail": the back pair at the tail's back corners, as far apart
    as they go, against tugs on the cables. "arm": all on the flanges, front, middle and back."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame()
    xs = xo + FLANGE / 2 + 1
    back = tail_frame()[2] - 9 if style == "tail" else y1 - 14
    return [(sx * xs, y) for sx in (-1, 1) for y in three_per_side(y0 + 14, back)]


def cradle_base(lip, beam, right_side_up=False, back_lip=None):
    """The cradle without its cable management: the full-length U with both flanges, an open frame for
    each side wall, a floor window leaving a `beam`-wide strip each side, and full-width lips (the back
    one `back_lip` tall if given)."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(right_side_up)
    cradle = strap(iw, ih, y0, y1, screws=False)   # holes are added by the caller
    # side walls: one open rectangle each, between the end posts and the thin top/bottom rails.
    # Printed standing on its front end, the back post spans the opening: supports hold it up.
    ya, yb, za, zb = y0 + POST, y1 - POST, -(TF + RAIL), -ih + RAIL
    cradle -= Box(2 * (xo + 1), yb - ya, za - zb, align=(C, MIN, MIN)).moved(Location((0, ya, zb)))
    # floor window. Its back edge spans the opening when printed standing up: supports hold it.
    wx = iw / 2 - beam
    cradle -= Box(2 * wx, yb - ya, T + 2, align=(C, MIN, MAX)).moved(Location((0, ya, -ih + 1)))
    # lips front and back, on the floor, full width, wall to wall (1 mm into each wall: one solid)
    cradle += Box(iw + 2, STOP_T, lip, align=(C, MIN, MIN)).moved(Location((0, y0, -ih)))
    cradle += Box(iw + 2, STOP_T, back_lip or lip, align=(C, MAX, MIN)).moved(Location((0, y1, -ih)))
    return cradle


def anchor():
    """A zip-tie anchor in its own frame: mounted on a face at z = 0, hanging into -z, centred on x = y = 0.
    A tunnel along x right against the face takes the tie; a groove along y on its underside seats the
    cable; its -y face is 45°, so it prints unsupported when y points up. -> (block, cuts)"""
    a = TUNNEL_W / 2 + 2
    apex = -ANCHOR_H                               # the groove's deepest point, under the tunnel's floor
    zt, zb = 1.0, apex - SADDLE_D
    side = Plane(origin=(-ANCHOR_W / 2, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))   # local (u, v) = (y, z)
    block = Polygon((-a - (zt - zb), zt), (a, zt), (a, zb), (-a, zb), align=None)
    cuts = (Box(ANCHOR_W + 2, TUNNEL_W, TUNNEL_H, align=(C, C, MAX))
            + Cylinder(SADDLE_R, 2 * (a + ANCHOR_H + SADDLE_D + 3), rotation=(90, 0, 0)).moved(
                Location((0, 0, apex - SADDLE_R))))
    return extrude(side * block, amount=ANCHOR_W, dir=(1, 0, 0)), cuts


def anchor_ref(d):
    """In an anchor's frame: a piece of cable of diameter d in its groove, and a zip tie through the
    tunnel, down both sides of the anchor and under the cable. -> (cable, tie)"""
    apex = -ANCHOR_H
    cable = Cylinder(d / 2, 40, rotation=(90, 0, 0)).moved(Location((0, 0, apex - d / 2)))
    hw, top, bot = ANCHOR_W / 2 + 0.05, -0.45, apex - d
    outer = Box(2 * (hw + TIE_T), TIE_W, top - (bot - TIE_T), align=(C, C, MAX)).moved(Location((0, 0, top)))
    inner = Box(2 * hw, TIE_W + 2, (top - TIE_T) - bot, align=(C, C, MAX)).moved(Location((0, 0, top - TIE_T)))
    return cable, outer - inner


def anchor_places(style):
    """Where the anchors go: a Location per anchor, taking its frame (face at z = 0, hanging into -z)
    into place. "tail": under the tail plate. "arm": on the inner face of the arm's end post, so they
    hang towards the cables (-x), tunnels running up and down."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame()
    if style == "tail":
        tie_y = tail_frame()[0]
        return [Location((x, tie_y, -TAIL_T)) for x in ANCHOR_X]
    y_end, tie_y, bottom = arm_frame()
    return [Location((xi, tie_y, bottom + h), (0, 90, 0)) for h in ARM_ANCHOR_UP]


def make_device(right_side_up=False):
    """The device in the cradle: upside down (feet up, DESK_GAP below the desk), or right side up on its
    feet, on the foam. Either way the stack is the same height, so the cradle is too."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(right_side_up)
    if right_side_up:
        bottom = -ih + FOAM_GAP + FEET_H
        device = device_body(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MIN)).moved(Location((0, 0, bottom))))
        feet_z, feet_align = bottom, MAX
    else:
        device = device_body(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MAX)).moved(Location((0, 0, body_top))))
        feet_z, feet_align = body_top, MIN
    for sx in (-1, 1):                             # the rubber strips
        device += Box(FEET_W, DEV_D - 10, FEET_H, align=(C, C, feet_align)).moved(
            Location((sx * (DEV_W / 2 - FEET_INSET), 0, feet_z)))
    return device


def make_cradle():
    """One part: the U-profile runs the full depth with continuous flanges, so both ends and all
    screw holes are fixed relative to each other. The device sits upside down on a foam pad, hanging
    free of the desk, held front and back by lips. Side and floor windows keep the fins open. A tail
    behind it, against the desk, carries the cable anchors.
    Install: foam, then the device, then screw the cradle up under the desk.
    -> (cradle, device)"""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame()
    cradle = cradle_base(CRADLE_LIP + FOAM_GAP, BEAM)

    # cable tail: the cradle's own side profile continues back: flanges and plate flush, the same
    # rounded outer edge, and the side walls carry on as short ribs, so the curve from flange to wall
    # runs the full length. The ribs' ends are cut at 45°. The opening behind the device (room to plug
    # in) ends in a 45° point, so it prints without support standing up.
    tie_y, a, y_end, point = tail_frame()
    zr = -(TAIL_T + TAIL_RIB)
    side = profile(
        [(-xf, 0), (xf, 0), (xf, -TF), (xo, -TF), (xo, zr), (xi, zr), (xi, -TF),
         (-xi, -TF), (-xi, zr), (-xo, zr), (-xo, -TF), (-xf, -TF)],
        corners=[(s * xo, -TF, 5) for s in (-1, 1)] + [(s * xf, -TF, 2) for s in (-1, 1)]
                + [(s * x, zr, 1) for s in (-1, 1) for x in (xi, xo)])
    tail = prism(side, y1, y_end)
    plan = Rectangle(2 * xf, y_end - y1 + 10, align=(C, MAX))
    plan = fillet(plan.vertices().sort_by(Axis.Y)[-2:], 6).moved(Location((0, y_end)))
    tail &= extrude(Plane.XY.offset(zr - 1) * plan, amount=-zr + 2, dir=(0, 0, 1))
    end = Plane(origin=(0, 0, 0), x_dir=(0, 1, 0), z_dir=(1, 0, 0))     # local (u, v) = (y, z)
    bevel = Polygon((y_end, -TF), (y_end + 5, -TF), (y_end + 5, zr - 5), (y_end - TAIL_RIB - 5, zr - 5), align=None)
    for sx in (-1, 1):
        cut = extrude(end.offset(xi - 1) * bevel, amount=xo - xi + 7, dir=(1, 0, 0))
        tail -= cut if sx > 0 else cut.mirror(Plane.YZ)
    opening = Polygon((-xi - 2, y1 - 2), (xi + 2, y1 - 2), (0, point), align=None)
    tail -= extrude(Plane.XY.offset(-TAIL_T - 1) * opening, amount=TAIL_T + 2, dir=(0, 0, 1))
    cradle += tail
    block, cuts = anchor()
    for loc in anchor_places("tail"):
        cradle += block.moved(loc)
        cradle -= cuts.moved(loc)
    for x, y in cradle_screws("tail"):             # after the tail: the back pair go through it
        cradle -= countersunk(x, y, -TF, TF)
    return cradle, make_device()


def make_sidearm():
    """The cradle with the device right side up (feet on the foam) and, instead of the tail, a tab off
    the +x side wall's back post, level with the ports, reaching ARM_L behind it, its inner face carrying
    the cable anchors. Only the flanges touch the desk. The ports are on the device's +x half (right side
    up); its exhaust on the -x half.
    -> (cradle, device)"""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(True)
    y_end, tie_y, bottom = arm_frame()
    cradle = cradle_base(CRADLE_LIP + FOAM_GAP + FEET_H, BEAM, True, BACK_LIP + FOAM_GAP + FEET_H)
    # front cross-bar across the top, wall to wall: with no tail, nothing else ties the U's two sides
    # together up at the flanges (sidearm v1 printed without it: the flanges' spacing wasn't held). As
    # tall as the bottom lip plus the floor under it, so from the front the two match (owner); the
    # cradle's extra height (SIDEARM_GAP) keeps it BAR_CLEAR above the grille.
    # It prints on the bed, the cradle standing on its front end.
    bar = T + FOAM_GAP + FEET_H + CRADLE_LIP
    cradle += Box(iw + 2, STOP_T, bar, align=(C, MIN, MAX)).moved(Location((0, y0, 0)))
    # the tab: the side wall carried on behind the back post, just over the anchors' height, its back
    # corners rounded. Standing on its front end to print, it grows straight up from the post: no supports.
    reach = ANCHOR_W / 2 + TIE_T + TAB_MARGIN
    zlo, zhi = bottom + min(ARM_ANCHOR_UP) - reach, bottom + max(ARM_ANCHOR_UP) + reach
    tab = Box(T, y_end - y1 + 1, zhi - zlo, align=(MIN, MIN, MIN)).moved(Location((xi, y1 - 1, zlo)))
    tab = fillet(tab.edges().filter_by(Axis.X).filter_by(lambda e: e.center().Y > y_end - 0.1), TAB_R)
    cradle += tab
    block, cuts = anchor()
    for loc in anchor_places("arm"):
        cradle += block.moved(loc)
        cradle -= cuts.moved(loc)
    for x, y in cradle_screws("arm"):
        cradle -= countersunk(x, y, -TF, TF)
    return cradle, make_device(right_side_up=True)


def foam(right_side_up=False):
    """Reference foam strips on the floor strips (beside the floor window), squeezed to FOAM_GAP, centred
    under the rubber feet (right side up, the feet stand on them), but kept on the strips."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(right_side_up)
    xc = min(DEV_W / 2 - FEET_INSET, iw / 2 - FOAM_W / 2 - 0.5)
    ya, yb = y0 + STOP_T + 0.5, y1 - STOP_T - 0.5
    return _union([Box(FOAM_W, yb - ya, FOAM_GAP, align=(C, MIN, MIN)).moved(
        Location((sx * xc, ya, -ih))) for sx in (-1, 1)])


def back_face(right_side_up=False):
    """The device's back, as placed: its plugs (as assumed in PLUGS) and the space behind its exhaust
    slots (EXHAUST), 60 mm deep. PLUGS and EXHAUST are given upside down (x as mounted, depth below
    its top); right side up, x flips and depth is height above its bottom. -> (plugs, exhaust space)"""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(right_side_up)
    bottom = -ih + FOAM_GAP + FEET_H
    at = (lambda x, d: (-x, bottom + d)) if right_side_up else (lambda x, d: (x, body_top - d))
    plugs = []
    for name, x, depth, (w, h), length, r in PLUGS:
        px, pz = at(x, depth)
        plugs.append(Box(w, length, h, align=(C, MIN, C)).moved(Location((px, DEV_D / 2, pz))))
    (ex0, ex1), (d0, d1) = EXHAUST
    xa, za = at(ex0, d0)
    xb, zb = at(ex1, d1)
    space = Box(abs(xb - xa), 60, abs(zb - za), align=(MIN, MIN, MIN)).moved(
        Location((min(xa, xb), DEV_D / 2, min(za, zb))))
    return _union(plugs), space


def anchor_refs(style):
    """A cable (the thinnest, the thickest, one between) and a tie at each anchor. -> (cables, ties)"""
    cables, ties = [], []
    for loc, d in zip(anchor_places(style), (CABLE_D[0], CABLE_D[1], sum(CABLE_D) / 2)):
        cable, tie = anchor_ref(d)
        cables.append(cable.moved(loc))
        ties.append(tie.moved(loc))
    return _union(cables), _union(ties)


def cradle_concept():
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame()
    tie_y, a, y_end, point = tail_frame()
    cradle, device = make_cradle()
    plugs, _ = back_face()
    cable_bits, ties = anchor_refs("tail")
    stand = Location((0, 0, 0), (90, 0, 0))        # print standing on its front end
    parts = [
        Part("cradle", cradle, color="#e07a3f", print_pose=stand),
        Part("device", device, color="#5b6068", reference=True, explode=(0, 0, -40)),
        Part("foam", foam(), color="#e8d44d", reference=True),
        Part("plugs", plugs, color="#3a6fd8", reference=True),
        Part("cables", cable_bits, color="#26282c", reference=True),
        Part("ties", ties, color="#f2f2ee", reference=True),
        Part("screws", _union([screw(x, y, -TF) for x, y in cradle_screws("tail")]), color="#b8bcc2", reference=True),
        Part("desk", desk(2 * xf + 40, 2 * y_end + 20).moved(Location((0, y_end / 2 - DEV_D / 4, 0))),
             color="#c8a978", reference=True, opacity=0.25),
    ]
    sheets = [Sheet("cradle", material=PETG, dims=[
        Dim("front", (-iw / 2, y0, -ih), (iw / 2, y0, -ih), "h", -16),
        Dim("front", (xi, y0, -ih), (xi, y0, 0), "v", 8),
        Dim("right", (xo, y0, -ih), (xo, y1, -ih), "h", -16),
        Dim("right", (xo, y1, 0), (xo, y_end, 0), "h", 8),
    ], notes=[Note("right", (xo, y1 - STOP_T / 2, -ih + CRADLE_LIP), f"lip {CRADLE_LIP + FOAM_GAP:g} high ({CRADLE_LIP:g} above the device), front and back",
                   side="above", along=-10),
              Note("top", (xo + FLANGE / 2 + 1, 0, 0),
                   f"{len(cradle_screws())}× countersunk for #6 flat-head screws", side="right", along=0),
              Note("top", (ANCHOR_X[-1], tie_y, 0), f"{len(ANCHOR_X)}× zip-tie anchor underneath, for 4.8 mm ties",
                   side="right", along=-20)])]
    detail = ("zip-tie anchors", (ANCHOR_X[2], tie_y, -TAIL_T - 4), 16)
    return parts, sheets, Plane.YZ, "Desk bracket — cradle (one part, upside down, lipped)", detail


def sidearm_concept():
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(True)
    y_end, tie_y, bottom = arm_frame()
    cradle, device = make_sidearm()
    plugs, _ = back_face(right_side_up=True)
    cable_bits, ties = anchor_refs("arm")
    lip = CRADLE_LIP + FOAM_GAP + FEET_H
    stand = Location((0, 0, 0), (90, 0, 0))        # print standing on its front end
    parts = [
        Part("cradle", cradle, color="#e07a3f", print_pose=stand),
        Part("device", device, color="#5b6068", reference=True, explode=(0, 0, -40)),
        Part("foam", foam(right_side_up=True), color="#e8d44d", reference=True),
        Part("plugs", plugs, color="#3a6fd8", reference=True),
        Part("cables", cable_bits, color="#26282c", reference=True),
        Part("ties", ties, color="#f2f2ee", reference=True),
        Part("screws", _union([screw(x, y, -TF) for x, y in cradle_screws("arm")]), color="#b8bcc2", reference=True),
        Part("desk", desk(2 * xf + 40, 2 * y_end + 20).moved(Location((0, y_end / 2 - DEV_D / 4, 0))),
             color="#c8a978", reference=True, opacity=0.25),
    ]
    sheets = [Sheet("cradle", material=PETG, dims=[
        Dim("front", (-iw / 2, y0, -ih), (iw / 2, y0, -ih), "h", -16),
        Dim("front", (-xi, y0, -ih), (-xi, y0, 0), "v", -8),
        Dim("right", (xo, y0, -ih), (xo, y1, -ih), "h", -16),
        Dim("right", (xo, y1, 0), (xo, y_end, 0), "h", 8),
    ], notes=[Note("right", (xo, y0 + STOP_T / 2, -ih + lip), f"lip {lip:g} high ({CRADLE_LIP:g} above the device), front and back",
                   side="above", along=-10),
              Note("top", (-(xo + FLANGE / 2 + 1), 0, 0),
                   f"{len(cradle_screws('arm'))}× countersunk for #6 flat-head screws", side="left", along=0),
              Note("right", (xo, y_end - ARM_POST / 2, bottom + ARM_ANCHOR_UP[1]),
                   f"{len(ARM_ANCHOR_UP)}× zip-tie anchor on the tab's inside, for 4.8 mm ties", side="right", along=0)])]
    detail = ("zip-tie anchors", (xi - 4, tie_y, bottom + ARM_ANCHOR_UP[1]), 30)
    return parts, sheets, Plane.YZ, "Desk bracket — cradle, right side up, cable tab", detail


def coupon_concept():
    """Fit test for the cradle: its base, cut straight out of the real cradle (floor, the bottom of
    the walls, both lips), so every surface the device touches is the cradle's own. Printed flat."""
    iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame()
    cradle, device = make_cradle()
    keep = lambda z0, z1: Box(2 * xf + 10, y1 - y0 + 10, z1 - z0, align=(C, C, MIN)).moved(Location((0, 0, z0)))
    coupon = cradle & keep(-ih - COUPON_FLOOR, -ih + COUPON_WALL)
    device = device & keep(-ih - 1, -ih + COUPON_DEVICE)       # just the device's (top) end, for the views
    zl = -ih + CRADLE_LIP + FOAM_GAP
    parts = [
        Part("coupon", coupon, color="#e07a3f"),                # prints as used: floor on the bed
        Part("foam", foam(), color="#e8d44d", reference=True),
        Part("device", device, color="#5b6068", reference=True, opacity=0.6, explode=(0, 0, 30)),
    ]
    sheets = [Sheet("coupon", material=PETG, dims=[
        Dim("top", (-xi, 0, -ih), (xi, 0, -ih), "h", 8),
        Dim("top", (xi, y0 + STOP_T, zl), (xi, y1 - STOP_T, zl), "v", 8),
        Dim("right", (xo, y0, -ih), (xo, y0, zl), "v", -8),
        Dim("right", (xo, y0, -ih - COUPON_FLOOR), (xo, y1, -ih - COUPON_FLOOR), "h", -10),
    ], notes=[Note("top", (0, y0 + STOP_T / 2, zl), f"lip {CRADLE_LIP + FOAM_GAP:g} high ({CRADLE_LIP:g} above the device), front and back",
                                    side="below", along=0)])]
    detail = ("front lip", (0, y0 + 6, -ih + 3), 14)
    return parts, sheets, Plane.YZ, "Desk bracket — cradle fit coupon", detail


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
        corners=[(s * xo, zb, 5) for s in (-1, 1)])
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

    device = device_body(Box(DEV_W, DEV_D, DEV_H, align=(C, C, MAX)).moved(Location((0, 0, dev_top))))
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


SLICER = {"cradle": {"enable_support": "1"},   # tree supports under the back posts, in the side openings
          "sidearm": {"enable_support": "1"}}   # the side and floor openings still need them


# ---------------------------------------------------------------- model

VARIANTS = ("cradle", "sidearm", "coupon", "upright", "inverted", "flat", "drawer")


def build(variant: str = "cradle") -> Model:
    if variant == "full":
        variant = "cradle"
    if variant not in VARIANTS:
        raise ValueError(f"variant must be one of {VARIANTS}")
    concept = {"drawer": drawer_concept, "inverted": inverted_concept, "cradle": cradle_concept,
               "coupon": coupon_concept, "sidearm": sidearm_concept}.get(variant, lambda: strap_concept(variant))
    parts, sheets, section, title, *detail = concept()
    return Model(name="desk_bracket", title=title, parts=parts, sheets=sheets, section=section,
                 checks=lambda r, p: checks(r, p, variant), slicer=SLICER.get(variant, {}),
                 detail=detail[0] if detail else None)


# ---------------------------------------------------------------- checks

def _overlap(a, b) -> float:
    return abs((a & b).volume) if a is not None else 0.0


def _play(fixed, moving, axis: int, sign: int, hi: float = 3.0, tol: float = 0.005) -> float:
    """How far `moving` can slide along +/- `axis` before it touches `fixed` (bisection)."""
    def hits(d):
        v = [0.0, 0.0, 0.0]
        v[axis] = sign * d
        return _overlap(fixed, moving.moved(Location(tuple(v)))) > 1e-4
    lo = 0.0
    if not hits(hi):
        return hi
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (lo, mid) if hits(mid) else (mid, hi)
    return lo


def _lift_to_clear(fixed, moving, push: float = 3.0, tol: float = 0.05, hi: float = 10.0) -> float:
    """How far `moving` must be lifted before it can be pushed `push` mm along -y (forward; negative: back)
    without a collision; `hi` if not even then."""
    lo = 0.0
    hits = lambda z: _overlap(fixed, moving.moved(Location((0, -push, z)))) > 1e-4
    while hi - lo > tol:
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if hits(mid) else (lo, mid)
    return hi


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

    if variant in ("cradle", "sidearm", "coupon"):
        # a device with sharp edges (0.2 mm), on the floor without foam, pushed against either wall
        iw, body_top, ih, xi, xo, xf, y0, y1 = cradle_frame(variant == "sidearm")
        sharp = device_body(Box(DEV_W, DEV_D, 10, align=(C, C, MIN)).moved(Location((0, 0, -ih))))
        flat = all(_overlap(brackets, mv(sharp, x=s * CLR)) < 1e-4 for s in (-1, 0, 1))
        report.check("device sits flat on the floor (sharp bottom edges, no foam)", flat,
                     "square inner corners: no contact anywhere but the floor, centred or against a wall")

    if variant == "coupon":
        report.dim("space under the device for foam (measured)", _play(brackets, dev, 2, -1, hi=5), FOAM_GAP, tol=0.03)
        report.check("device: supported (on the foam)", _overlap(brackets + parts["foam"].shape, mv(dev, z=-0.5)) > 1,
                     "lowering it 0.5 mm collides")
        report.check("device drops in from above", _overlap(brackets, mv(dev, z=COUPON_DEVICE + 5)) < 1e-4)
        for label, axis, want in (("sideways", 0, CLR), ("front/back", 1, CRADLE_CLR_Y)):
            plays = [_play(brackets, dev, axis, s) for s in (-1, 1)]
            report.dim(f"play {label}, each way (measured)", min(plays), want, tol=0.03)
        # the lips: they must still stop the device at its rounded edge. Measure how far up the device's
        # end face the lip reaches: lift the device until it clears the front lip when pushed forward.
        lift = _lift_to_clear(brackets, dev)
        report.dim("lips: lift to clear them (measured)", lift, CRADLE_LIP, tol=0.1)
        cradle, _ = make_cradle()
        same = abs((cradle & brackets).volume - brackets.volume) < 1e-3
        report.check("coupon is the cradle's own geometry", same, "coupon ⊂ cradle")
        return

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
    elif variant in ("cradle", "sidearm"):
        arm = variant == "sidearm"
        desk_ = parts["desk"].shape
        up = _play(desk_, dev, 2, 1, hi=10)
        report.dim("air between the device and the desk (measured)", up, SIDEARM_GAP if arm else DESK_GAP, tol=0.03)
        for way, push in (("front", 3.0), ("back", -3.0)):
            clear = _lift_to_clear(brackets, dev, push)
            report.check(f"device can't escape over the {way}", clear > up + 1,
                         f"it must lift {'more than ' if clear >= 9.9 else ''}{clear:.1f} mm; the desk stops it at {up:.1f} mm")
        report.dim("space under the device for foam (measured)", _play(brackets, dev, 2, -1, hi=5), FOAM_GAP, tol=0.03)
        report.check("device: supported (on the foam)", _overlap(brackets + parts["foam"].shape, mv(dev, z=-0.5)) > 1,
                     "lowering it 0.5 mm collides")
        report.check("device: lips hold it front and back",
                     _overlap(brackets, mv(dev, y=-(CRADLE_CLR_Y + 1))) > 0.01 and _overlap(brackets, mv(dev, y=CRADLE_CLR_Y + 1)) > 0.01)
        report.check("device: held sideways", _overlap(brackets, mv(dev, x=1.5)) > 0.01)
        report.check("device drops in from above (before mounting)",
                     _overlap(brackets, mv(dev, z=DEV_H + 10)) < 1e-4)
        # cable anchors
        plugs, ties = parts["plugs"].shape, parts["ties"].shape
        report.check("plugs clear of the cradle", _overlap(brackets, plugs) < 1e-3, f"{_overlap(brackets, plugs):.4f} mm³")
        report.check("plugs pull straight out", _overlap(brackets, mv(plugs, y=max(p[4] for p in PLUGS) + 5)) < 1e-3)
        screws_ = parts["screws"].shape.solids()
        recess = [_play(brackets, sc, 2, 1, hi=3) for sc in screws_]   # how far up each head goes before it seats
        flush = all(_overlap(brackets, sc) < 1e-3 for sc in screws_) and max(recess) < 0.6
        report.check(f"#6 screws seat in all {len(screws_)} countersinks", flush,
                     f"heads sit {min(recess):.2f}–{max(recess):.2f} mm below flush (head {SCREW_HEAD:g} mm, "
                     f"countersink {CSK_D:g} mm, {CSK_ANGLE:g}°)")
        report.check("screws stay inside the desk", SCREW_L - TF < DESK_T,
                     f"{SCREW_L - TF:.1f} mm into the desk; it must be thicker than that (assumed {DESK_T:g})")
        cables_ = parts["cables"].shape
        # the anchors' frames: towards the face they hang from (tail: up; arm: +x), and across the groove
        inward = (lambda c, d: mv(c, x=d)) if arm else (lambda c, d: mv(c, z=d))
        across = (lambda c, d: mv(c, z=d)) if arm else (lambda c, d: mv(c, x=d))
        seated = [_overlap(brackets, c) < 1e-3 and _overlap(brackets, inward(c, 0.05)) > 1e-4
                  and all(_overlap(brackets, across(c, s * 0.5)) > 1e-3 for s in (-1, 1)) for c in cables_.solids()]
        report.check(f"cables {CABLE_D[0]:g}–{CABLE_D[1]:g} mm seat in the anchors' grooves", all(seated),
                     "each sits up in its groove, clear of the cradle, and can't slide 0.5 mm sideways")
        report.check("zip ties pass through the anchors", _overlap(brackets, ties) < 1e-3
                     and all(_overlap(brackets, inward(t, -2.0)) > 0.1 for t in ties.solids()),
                     "clear of the cradle, and trapped: pulling each tie 2 mm off its anchor collides")
        behind = back_face(right_side_up=arm)[1]
        report.check("exhaust airflow clear (60 mm behind the slots)", _overlap(brackets, behind) < 1e-3,
                     "slot area assumed from the photo")
        top = brackets & Box(400, 400, 1.0, align=(C, C, MAX)).moved(Location((0, 0, -1.0)))   # a slice 1–2 mm down
        report.check("the U's two sides are tied together at the top", len(top.solids()) == 1,
                     f"a slice just under the desk is {len(top.solids())} piece(s)")
        touching = brackets & Box(400, 400, 0.2, align=(C, C, MAX))      # the top 0.2 mm: what's against the desk
        report.check("area against the desk", True, f"{abs(touching.volume) / 0.2 / 100:.0f} cm²")
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
    border = CRADLE_BORDER if variant in ("cradle", "sidearm") else BORDER
    face = dev
    if variant in ("cradle", "sidearm"):           # the faces are the body's: leave out the rubber feet
        ih, body_top = cradle_frame(variant == "sidearm")[2], cradle_frame(variant == "sidearm")[1]
        z0 = -ih + FOAM_GAP + FEET_H if variant == "sidearm" else body_top - DEV_H
        face = dev & Box(DEV_W + 2, DEV_D + 2, DEV_H, align=(C, C, MIN)).moved(Location((0, 0, z0)))
    for name, side in (("front", -1), ("back", +1)):
        if name == "front" and variant in ("cradle", "sidearm"):
            # the front's grille, as measured: between FRONT_SOLID_FEET from the feet-side plate and
            # FRONT_SOLID_TOP from the top plate (sides: CRADLE_BORDER, assumed)
            ih, body_top = cradle_frame(variant == "sidearm")[2], cradle_frame(variant == "sidearm")[1]
            if variant == "sidearm":       # right side up: feet-side plate at the bottom
                feet_side = -ih + FOAM_GAP + FEET_H
                z0, z1 = feet_side + FRONT_SOLID_FEET, feet_side + DEV_H - FRONT_SOLID_TOP
            else:                          # upside down: feet-side plate at the top
                z0, z1 = body_top - DEV_H + FRONT_SOLID_TOP, body_top - FRONT_SOLID_FEET
            grille = Box(DEV_W - 2 * CRADLE_BORDER, DEV_D, z1 - z0, align=(C, C, MIN)).moved(Location((0, 0, z0)))
            cov = face_coverage(grille, brackets, 1, side)
            report.check("front grille open (measured solid border)", cov < 0.005, f"{100 * cov:.1f} % covered")
            continue
        if name == "back" and variant in ("cradle", "sidearm"):
            # the back, from where the ports start (PORTS_SPAN[0] from the feet-side plate, measured) to
            # CRADLE_BORDER from the top plate: ports, exhaust slots. Below the ports it's solid.
            ih, body_top = cradle_frame(variant == "sidearm")[2], cradle_frame(variant == "sidearm")[1]
            if variant == "sidearm":
                feet_side = -ih + FOAM_GAP + FEET_H
                z0, z1 = feet_side + PORTS_SPAN[0], feet_side + DEV_H - CRADLE_BORDER
            else:
                z0, z1 = body_top - DEV_H + CRADLE_BORDER, body_top - PORTS_SPAN[0]
            open_ = Box(DEV_W - 2 * CRADLE_BORDER, DEV_D, z1 - z0, align=(C, C, MIN)).moved(Location((0, 0, z0)))
            cov = face_coverage(open_, brackets, 1, side)
            report.check(f"back open from the ports up ({PORTS_SPAN[0]:g} mm, measured)", cov < 0.005,
                         f"{100 * cov:.1f} % covered")
            continue
        cov = face_coverage(face, brackets, 1, side, border)
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
    screws = len(cradle_screws("arm" if variant == "sidearm" else "tail")) if variant in ("cradle", "sidearm") else 4
    report.check("hangs below the desk", True, f"{drop:.0f} mm")
    report.check("desk footprint", True, f"{allb.size.X:.0f} × {allb.size.Y:.0f} mm")
    report.check("screws", True, f"{screws}, {DEV_MASS * 9.81 / screws:.1f} N each (the device's weight shared)")
