# Desk bracket — design brief

## Purpose
Mount an OWC Express 4M2 Ultra (Thunderbolt 5, 4× NVMe) under the desk.
**Chosen: `--variant cradle`** (the default). It combines the earlier concepts,
which are kept as variants for reference: `upright`, `inverted`, `flat`
(rejected: fins horizontal, poor cooling), `drawer` (rejected: too complex;
easy removal isn't needed).

## The device
| | value | source |
|---|---|---|
| width | 60 mm | published (2.36 in) — **measure to confirm** |
| height | 123 mm | published (4.84 in) — **measure to confirm** |
| depth | 117 mm | published (4.60 in) — **measure to confirm** |
| mass | 0.9 kg | published |
| edge radius | 3 mm | **assumed** |

From the owner:
- Air flows **front → back** (fan draws in at the front; ports and exhaust at
  the back). Front and back must stay open, except a border of a few mm
  around the edge (`BORDER` = 3 mm), which may be covered.
- The **left and right sides are aluminium radiator fins**: cover as little
  of them as possible.
- Top and bottom are flat plates. The bottom has **two rubber strips** running
  front to back (its feet).

From the owner's photos (front, side, back):
- Front: perforated grille; a solid strip ~25 mm tall at the bottom with the logo.
- Sides: the **fins run vertically**, between solid rounded columns ~8 mm wide
  at the front and back edges. Upright, warm air rises through the fins like
  a chimney; on its side the fins are horizontal and lose that.
- Back: ports in the lower middle, exhaust slots on the right, lock slot at
  the bottom right, a screw in each corner. Cables leave straight back and bend
  down, so leave room behind it.

## Axes
X = left→right, Y = front→back (front = −Y, facing you; ports at +Y), Z = up.
The desk underside is z = 0; everything hangs below it.

## Concepts
- **cradle** (chosen) — one part. The U-profile runs the full depth with
  continuous screw flanges, so the ends and all 6 screw holes are fixed relative
  to each other and it sits flat against the desk (from the drawer). The device
  sits upside down with its rubber feet pressed 0.4 mm into the desk (owner's
  idea; no rattle), held by 4 mm **lips** front and back (from upright). Each
  side is an open frame: 12 mm end posts (over the edge columns) and 6 mm
  rails top and bottom, ~90 % of the fin area open. The floor window has a 45°
  point at its back end, so it prints as its own roof. (Pointed side windows
  with cross-bars printed without supports but covered 25 % of the fins; the
  owner preferred open sides with supports.) Install: drop the
  device in, then screw the cradle up under the desk; tightening the screws
  presses the feet into the desk. Tip: hold the empty cradle up as a drilling
  template for pilot holes first.
- **upright** (recommended) — two U-straps screwed to the desk; the device stands in them on
  its rubber feet, as on a desk. Straps are 14 mm wide so their arms sit on the
  solid edge columns rather than the fins. Each strap: a flange each side with one
  countersunk screw, arms down the fin faces, a floor under the device. The
  device slides in from the front, lifted 3 mm over a 2.5 mm **front lip**,
  and stops against a 2.8 mm **back stop**. Hangs ~135 mm below the desk.
- **inverted** (owner's idea) — upside down: the straps press the rubber feet
  0.5 mm into the desk underside. Held by the rubber's friction, so no lips at
  all; a 1.5 mm ramp on the front strap's floor helps push it in. No rattle.
- **flat** — the same straps sized for the device on its side (fins facing up
  and down). Hangs ~75 mm below the desk. One fin face rests on the straps;
  the other faces the desk 3.5 mm away.
- **drawer** — two rails screwed to the desk and an upright **cage** (front
  and back U-frames joined by floor beams) that the device drops into. The
  frames' **runners** have a 45° underside that rests on a matching 45° slope
  on each rail (a V-slide: self-centring, and prints without supports). A
  ridge on each rail's slope clicks into a notch in the front runner; a stop at
  the back of each rail. Pull it out by the **handle** to take the drive away.

## Printing
- Every part is a cross-section extruded front to back, printed standing on
  its end, so each layer contains the whole load path (tension along the
  strands, not across layer lines). Exception: the drawer's cage prints
  upright, as used (floor beams on the bed).
- The cradle needs tree supports (on in its project file) under the back
  posts, inside the side openings: 181 min, 81 g.
- Material: **PETG** recommended (the device runs warm and the load is
  constant; PLA slowly sags). The project file uses the PLA preset: switch
  the filament to Generic PETG in Bambu Studio before slicing.
- Screws: 4 mm (#8) countersunk wood screws, shorter than the desktop is thick.

## Checks (all measured on the geometry)
No interference with the device; the device is supported, stopped front and
back, and can be removed by lifting it less than the space available; front
and back faces open inside the border; fin coverage reported.

## Open questions
- Confirm the dimensions and where the rubber strips are (inverted assumes
  8 mm wide, 1 mm tall, 10 mm in from each side).
- Drawer: the cage's frames print as free-standing 130 mm posts; watch for
  wobble near the top.
- Cradle: is a 0.4 mm squeeze right for the rubber feet? Too much and the
  cradle bows; too little and it rattles. `CRADLE_PRELOAD`.
- Cradle: the 4 mm lips assume the solid border at the device's top edge is
  ~9–10 mm (from the photos). `CRADLE_BORDER` is the check's 6 mm allowance.
