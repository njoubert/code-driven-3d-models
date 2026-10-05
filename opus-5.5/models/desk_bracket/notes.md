# Desk bracket — print log

Record every print here: date, variant, settings, what fit, what changed.
The sliced Bambu Studio project for each print is kept in `prints/`.

| date | variant | printer / material | settings | project file | result | change made |
|---|---|---|---|---|---|---|
| 2026-10-03 | coupon: `CLR` 0.6, `CLR_Y` 0.5, `CRADLE_LIP` 6 | P2S 0.4, PETG | 0.20mm Standard, 2 walls, 15% grid, no supports | not saved | Width perfect. Length a little loose: 7 sheets of HP Premium32 (0.132 mm) fit end to end, not 8 = 0.92–1.06 mm slack, as modelled (1.0). Lips hold it. | `CRADLE_CLR_Y` 0.5 → 0.2 (cradle only): expect 3 sheets, not 4 |
| 2026-10-03 | coupon v2: `CLR` 0.6, `CRADLE_CLR_Y` 0.2, `CRADLE_LIP` 6 | P2S 0.4, PETG | 0.20mm Standard, 2 walls, 15% grid, no supports | not saved | Fits great: width and length right, lips hold it. | None to the fit. Since then (not in this coupon): 2 mm foam gap under the device, lips 8 mm off the floor |
| 2026-10-04 | cradle v1: `CLR` 0.6, `CRADLE_CLR_Y` 0.2, `CRADLE_LIP` 6 (+2 foam), 2.5 mm inner corner fillets | P2S 0.4, PETG | 0.20mm Standard, tree supports | not saved | Device doesn't sit flat: its sharp 90° bottom edges ride on the floor-to-wall fillets (felt tight). ~1 mm sideways slop at the top (the designed 1.2 mm total). Length fine. | Fillets → square corners; `CLR` 0.6 → 0.2; device modelled with sharp edges. Coupons v1/v2 were fooled by the same fillets |
| 2026-10-04 | sidearm v1: right side up, cable tab 45 mm, `CLR` 0.2, square corners | P2S 0.4, PETG | 0.20mm Standard, tree supports | not saved | Generally pleased. Major: with no tail, nothing ties the U's two sides together at the top, so the spacing between the flanges' screw holes isn't held. Minor: the tab is a little short. | Front cross-bar across the top (the front lip, mirrored); tab 45 → 63 mm |
