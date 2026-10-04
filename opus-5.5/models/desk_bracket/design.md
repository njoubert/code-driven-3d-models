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
| width | 60 mm | published (2.36 in); coupon v1 fit as modelled |
| height | 122.12 mm | measured (calipers), body without the rubber feet; published 123 |
| rubber feet | 1.24 mm tall | measured (123.36 with feet); width 8 mm and position **assumed** |
| feet compliance | none | owner: the rubber has no noticeable give, so it can't be the spring: foam under the device is |
| depth | 117 mm | published (4.60 in); confirmed by coupon v1 (slack measured as modelled) |
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
  continuous screw flanges, so the ends and all screw holes are fixed relative
  to each other and it sits flat against the desk (from the drawer). The device
  sits upside down with its rubber feet against the desk (owner's idea),
  on **foam**: the floor is 2 mm below the device (`FOAM_GAP`, owner's
  choice), filled with foam strips on the floor strips, which press the device
  against the desk and take up height errors (the feet have no give). Held by
  **lips** front and back (from upright) that reach 6 mm up its end faces,
  so they stand 8 mm off the floor. Each
  side is an open frame: 12 mm end posts (over the edge columns) and 6 mm
  rails top and bottom, ~90 % of the fin area open. The floor has a plain
  rectangular window. (Pointed windows with cross-bars printed without
  supports but covered 25 % of the fins; the owner preferred open sides and
  floor with supports.) Install: drop the
  foam, then the device, then screw the cradle up under the desk; tightening
  the screws squeezes the foam. Foam: closed-cell (EVA or neoprene weatherstrip
  tape), ~3 mm thick so it is squeezed ~1 mm, ~9 mm wide. Tip: hold the empty cradle up as a drilling
  template for pilot holes first.
  **Cable tail** (owner chose option A of three: tail plate / tie bar below the
  ports / separate clip): the cradle's side profile continues 52 mm back: the
  plate is flush with the flanges (5 mm), with the same rounded outer edge, and
  the side walls carry on as 7 mm ribs (ends cut at 45°), so the curve from
  flange to wall runs the full length. A triangular opening behind the device
  (its 45° point prints without support), then a row of three zip-tie anchors
  underneath, between the ribs, 20 mm apart for room to thread the ties
  (tunnels for 4.8 mm ties). The owner puts a loop in each
  cable before tying it to an anchor: the loop takes the strain off the
  connectors, so the anchors needn't be placed for a particular cable bend.
  2 more screws at the plate's back corners (8 in all). **Assumed** from the
  back photo, to measure: ports in a column ~9 mm off centre, power plug
  16–25 mm and the screw-locked Thunderbolt plug 32–44 mm below the device's
  top (as mounted), plugs 25 / 28 mm long; exhaust slots beside the ports,
  30–81 mm down. The checks keep the plugs and the space behind the exhaust
  clear (`PLUGS`, `EXHAUST`).
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

## Fit coupon (`--variant coupon`)
The cradle's base, cut straight out of the cradle model: the floor (thinned to
1.6 mm under the device), the bottom 10 mm of the walls and both lips. Print it
flat, no supports (~30 min, ~16 g), and set the device into it upside down.
Every surface the device touches is the cradle's own, so a good fit here is a
good fit in the cradle. Check:
- **Width** (61.2 mm between the walls; 0.6 mm play each side, `CLR`): it
  should drop in without forcing and wiggle only slightly sideways.
- **Length** (117.4 mm between the lips; 0.2 mm play each end, `CRADLE_CLR_Y`):
  it should drop in between the lips without forcing and barely move front to
  back. Feeler: HP Premium32 paper is 0.132 mm, so 3 sheets should fit end to
  end, not 4. (v1 had 0.5 mm each end: 7 sheets fit, too loose.)
- **Lips** (8 mm off the floor, 6 mm above the device on its 2 mm of foam):
  they should catch the device's end faces above its rounded edge and not cover
  the front grille or the ports. Coupon v2 predates the foam gap (6 mm lips,
  device on the floor): it still tests width and length.
Print it in the same filament as the cradle (PETG): shrinkage differs between
materials. The cradle prints standing on end, so its length is built up in
layers, while the coupon's is printed flat: expect a difference of a tenth of
a millimetre or two.

## Printing
- Every part is a cross-section extruded front to back, printed standing on
  its end, so each layer contains the whole load path (tension along the
  strands, not across layer lines). Exception: the drawer's cage prints
  upright, as used (floor beams on the bed).
- The cradle needs tree supports (on in its project file) under the back
  posts and the back lip, inside the side and floor openings: 227 min, 98 g
  with the cable tail.
- Material: **PETG** recommended (the device runs warm and the load is
  constant; PLA slowly sags). The project file uses the PLA preset: switch
  the filament to Generic PETG in Bambu Studio before slicing.
- Screws: 4 mm (#8) countersunk wood screws, shorter than the desktop is thick.

## Checks (all measured on the geometry)
No interference with the device; the device is supported, stopped front and
back, and can be removed by lifting it less than the space available; front
and back faces open inside the border; fin coverage reported.

## Open questions
- Where the rubber strips are and how wide (assumed 8 mm wide, 10 mm in from
  each side). Nothing depends on it now that the foam is the spring.
- Drawer: the cage's frames print as free-standing 130 mm posts; watch for
  wobble near the top.
- Cradle: foam thickness and stiffness: enough to hold 0.9 kg against the desk
  without the cradle bowing. Try ~3 mm closed-cell foam in the 2 mm gap.
- Cradle: the lips reach 6 mm up the device, exactly to `CRADLE_BORDER`, the check's 6 mm
  allowance for the solid border at the device's top edge (~9–10 mm in the
  photos). Measure the border: if it is that wide, the lips could go to ~8 mm.
