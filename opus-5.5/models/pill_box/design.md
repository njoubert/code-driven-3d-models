# Pill box — design brief

## Purpose
Hold one Zoloft 100 mg tablet per day for a week, Monday to Sunday, in a
small box that can sit on a desk or go in a bag.

## The pill
| | value | source |
|---|---|---|
| length | 13.0 mm | measured 2026-10-03 (drugs.com also says 13 mm) |
| width | 6.0 mm | measured 2026-10-03 |
| thickness | 5.0 mm | measured 2026-10-03 |

The pocket (11 × 17 × 6.5) leaves room around the pill so it tips out easily.

## Shape and named parts
Axes: X = left→right along the row of days, Y = front→back, Z = up.
Front (−Y) is the face with the day letters. Monday is at −X.

- **base** — one row of 7 **pockets**, separated by **dividers**. The
  **Monday end wall** is closed; the **Sunday end** is open at lid height.
- **pocket** — 11 × 17 mm, 6.5 mm deep. The pill lies front-to-back.
  Rounded vertical corners (R3) and a rounded floor edge (R2.5) so the pill
  slides out when you tip the box into your hand.
- **lid slot** — a dovetail running along the top of the base: wider at the
  bottom than the top, so the lid can't lift out, only slide.
- **lid** — a flat dovetail strip that slides out through the Sunday end.
  Push it towards Sunday a day at a time: Monday is exposed first.
  **Grip grooves** and an **arrow** near the Monday end show which way it goes.
- **day letters** — M T W T F S S engraved 0.5 mm into the front face.

## Fit
- Lid running clearance: 0.25 mm per side, horizontal (`LID_CLEARANCE`).
  This is the number most likely to need tuning — print the coupon first.
- Lid rests on the 1.2 mm ledges either side of the pockets and on the
  divider tops, so a pill can't move between days.

## Printing
- Printer: Bambu Lab P2S (256 × 256 × 256 mm).
- Material: PLA is fine (no load, room temperature).
- base: as it sits, floor on the bed. The dovetail's overhang is ~31° from
  vertical, so no supports.
- lid: flat, wide face down. No overhangs.
- 0.4 mm chamfer on the base's bottom edge to counter elephant's foot.

## Open questions
- Does the lid need a detent so it can't slide open in a bag? Not in v1;
  decide after handling the coupon.
