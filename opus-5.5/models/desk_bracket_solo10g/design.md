# Solo10G desk bracket — design brief

## Purpose
Hang a Sonnet Solo10G (Thunderbolt 3 to 10 GbE adapter) under the desk. Same
idea as `desk_bracket`'s cradle for the OWC drive, but simpler: no cable
anchors, no foam, no feet. **`--variant cradle`** (the default) is the part;
`--variant coupon` tests its fit.

## The device
| | value | source |
|---|---|---|
| width | 79.6 mm | measured (calipers), across the side fins |
| height | 24.6 mm | measured, base plate to the top fins' tips |
| depth | 99.1 mm | measured, front plate to back plate (102.1 over the plates' screw heads) |
| end plate screw heads | stand 1.5 mm proud of each plate | measured (102.1 − 99.1); they sit in the open between the lips and the top bars (owner, first test print), so the lips fit the plates themselves |
| Ethernet (RJ45) jack, front | centred left/right; 4.9–16.9 mm down from the top | measured |
| Ethernet jack width | 16 mm | **assumed** |
| Thunderbolt 3 port, back | centred left/right; its bottom edge 7.6 mm above the base | measured |
| Thunderbolt port opening | 8.4 × 2.6 mm (USB-C) | **assumed** (standard) |
| mass | 0.24 kg | published (Sonnet: 0.54 lb) |
| fins | top, left and right; none on the front, back or base | owner |
| fin direction | front to back, from the front plate to the back plate | owner; depth and pitch **assumed** (drawn 2 mm deep, 4 mm pitch, for the views only) |
| end plates | 4 mm, cover the fin channels' ends | **assumed** |
| edges | sharp | **assumed** (the inner corners are square anyway) |
| cooling | passive: no fan, no feet | owner |

Published size is 79.5 × 114 × 27.2 mm. The owner measured the depth and height
smaller than that. The measured values are used here.

Plugs (all **assumed**): the RJ45 plug and boot fit within a box 14 mm wide × 12 mm
tall × 40 mm long, centred on the jack. The Thunderbolt plug's moulding is
12 × 6.5 × 30 mm, centred on the port.

## Axes
X = left→right, Y = front→back (front = −Y, the Ethernet side), Z = up.
The desk underside is z = 0; everything hangs below it.

## The cradle
The device hangs **upside down**, as the owner suggested. The base plate, which
has no fins, faces the desk with **5 mm of air** above it (`DESK_GAP`, owner).
The top fins face down into open room air, and the side fins face out
sideways.

One part. A flat rectangular frame lies just under the desk: the two
**flanges**, a **side strip** along the top of each side wall, and a **top
bar** across each end. The sides of the frame stand 3 mm off the desk. Only
the four **pads**, one above each post where the screws go, and the top bars
between them touch the desk. A matching frame lies under the device: a
**floor bar** across each end and a **floor rail** under each side wall. The
two frames are joined by four **posts**. Seen from the side it is an open
rectangle. Everything along the device's length between the end frames is
open.

- **Air pocket.** The 5 mm of air between the base plate and the desk gets
  warm, and warm air can only leave sideways, along the underside of the desk.
  The flanges and side strips therefore **stand 3 mm off the desk**
  (`STANDOFF`; they are `TF` 4 mm thick). That leaves a slot at desk level
  along each side, under the flanges. Measured at the tightest section, 49 % of
  each side of the pocket is open (250 mm²); the pads take the rest. The ends
  are closed: the top bars reach the desk (owner: a 4 mm bar hanging 3 mm under
  the desk would snap off with its supports). When the whole frame lay flat
  against the desk (the first draft), the pocket was sealed on all four sides.
- **Pads**: 20 × 10.7 mm, over the posts. Their inner ends slope at 45° down
  into the flange, all four alike (owner: symmetric). Printed standing on the
  front end, the back two then build up out of the flange without supports.

- **Floor bars** run across the front and back ends, `HOLD` (8 mm) under the
  device. Upside down, the device rests on its top fins' tips there.
- **Posts** reach `HOLD` along the device's sides from its ends. They hold
  it left/right.
- **Floor rails** sit under the side walls, outside the device's width and
  below it, so they cover no fins. They tie the two floor bars together.
  **6 × 6 mm** (`T`, as are the posts, side walls and floor bars; was 4): a
  4 × 4 rail (~15 mm², with its corner rounded) broke off in test fitting.
  Printed standing on end, a rail's layers stack along its length, so bending
  it pulls the layers apart; it needs the extra section. The window corners
  where the rails meet the posts are rounded to 6 mm (was 4). Checked: each rail
  measures 35 mm² at mid-span (at least 30).
- **Lips** at each end reach `LIP` (4 mm) up the end faces from the floor, full
  width, 4 mm thick (`STOP_T`; was 2.5). They stay under the Ethernet jack (4.9 mm up; 0.9 mm to spare), so the
  plug needs no notch (owner), and well under the Thunderbolt plug.
- **Top bars** at the ends lie just beyond the device's ends, from the desk
  down to 7 mm under it, pad to pad, 4 mm thick. They overlap the top 2 mm of
  its end faces (the side strips do the same at the sides), well clear of the
  Thunderbolt port (7.6 mm down).
- Front to back, the lips and the top bars hold the device between them.
  Sitting on the floor bars, the lips stop it. Lifted at all, its top edge
  meets the top bars before it can slide. So the lips needn't be taller than
  the 5 mm it can lift. (The first draft, never printed, had 7 mm lips with a
  notch for the plug.) Checked at every lift from 0 to 5 mm: it slides 0.2 mm
  at most.
- Install: drop the device in, then screw the cradle up under the desk. Tip:
  hold the empty cradle up as a drilling template for the pilot holes.

## Fit
- Across: 0.2 mm per side (`CLR`), as on the OWC cradle, which fit well.
- Front to back: 0.2 mm per end (`CLR_Y`): 99.5 mm between the lips for the
  99.1 mm between the plates. (Until the first test print the lips were sized
  over the screw heads, 102.1 mm.)
- Inner corners are square, so a sharp-edged device sits flat on the floor bars.

## Fit coupon (`--variant coupon`)
The cradle's bottom 10 mm, cut straight out of the cradle: floor bars, floor
rails, lips, and the posts' lower ends. Print it flat, no supports. Set the
device into it upside down and check:
- **Width**: it drops in between the posts without forcing and wiggles only slightly sideways.
- **Length**: it drops in between the lips and barely moves front to back.
  0.4 mm of play in total: 3 sheets of HP Premium32 (0.132 mm) should fit at one end, not 4.
- **Ethernet**: a plug goes in and out over the front lip, and you can press its latch.
  The coupon has no top bars, so it doesn't test the hold: lifted 4 mm, the device comes out.

## Printing
- Material: **PETG** (the device runs warm). The project file loads the PLA
  preset: switch to Generic PETG in Bambu Studio before slicing.
- The cradle prints standing on its front end, like the OWC cradle, so each
  layer contains the load path. Tree supports (on in the project file) hold
  up the back end frame's bars (top bar, floor bar, lip). About 2 h 13 min, 48 g.
  124 × 107.5 mm on the desk, 35.6 mm below it.
- Screws: 4 #6 × 5/8" flat-head screws, one through each pad. The pad and the
  flange are 7 mm thick together, so each screw reaches 8.9 mm into the desk.
  The device weighs 0.24 kg; any one screw alone could hold it many times over.
  Use 3/4" screws for a soft or thin desktop.

## Open questions (to measure or confirm)
- Are the fin channels open at the ends, or
  closed by the end plates? If they're open, the 4 mm lips cover the bottom of
  the channels' ends.
- Edge shape: sharp, or rounded (which edges, what radius)? A rounded edge at the
  base plate would meet the top bars lower down, so they'd catch less of it.
- Fin depth and pitch, and how far in from each end the fins start (where
  the posts and floor bars touch).
- Screw heads on the end plates: where exactly, and how wide? They clear the
  lips and the top bars in the test print. With their positions, a check could
  keep them clear if the lips or bars change.
- Ethernet jack width, and which way its latch faces. Any status LEDs on the
  front?
- Do you use the ThunderLok-S retainer on the Thunderbolt cable? It needs
  room at the back.
