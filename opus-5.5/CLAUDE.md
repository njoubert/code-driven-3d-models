# Code-driven 3D models (opus-5.5)

3D-printable models written as Python with build123d (B-rep CAD on
OpenCascade). Work only inside this folder, except `../.vscode/` (VS Code
only reads it at the repo root). `../gpt-5.3/` is an older,
separate approach (trimesh mesh CSG); don't modify it.

## Conventions
- Units: millimetres.
- Axes in **use pose** (how the object sits when used): X = left→right,
  Y = front→back (front = −Y, the side facing the user), Z = up.
- Print pose is separate: set per part with `Part.print_pose`; the harness
  drops it onto z=0.
- Parameters are UPPER_CASE constants at the top of `model.py`, named after
  the parts in `design.md` (e.g. `LID_CLEARANCE`, not `c2`). Keep the
  measured size of a real object separate from the clearance added to it.
- Mark any dimension that wasn't measured as **assumed** in `design.md`.

## Layout
```
common/            harness: model types, checks, export, render, drawing, run
models/<name>/
  design.md        brief: purpose, measurements, named parts, fit, printing
  model.py         build(variant) -> Model; model-specific checks
  notes.md         print log: what was printed, what fit, what changed
  out/<variant>/   generated, but committed: rerun before committing so it matches the code
  prints/          Bambu Studio projects as actually printed (YYYY-MM-DD_<variant>_vN.3mf); never regenerated
```

## The loop: do this after every geometry change
```
.venv/bin/python -m common.run <name> [--variant coupon] [--fast]
```
1. All checks must PASS. A WARN needs a sentence of explanation.
2. Look at `out/<variant>/render_sheet.png` (6 views incl. cutaway and
   print plate) and say what you checked in it. Models with small features
   set `Model.detail` and also get `render_detail.png`: look at that too.
3. For a change to the geometry or dimensions, also look at the
   `drawing_<part>.png` sheets.
4. Report key numbers from the check output, not from the parameters.

Images catch gross errors (wrong face, missing feature, wrong
orientation). Sizes are verified by the checks: when adding a feature with a
fit requirement, add a check that **measures the geometry** (sections, rays,
boolean interference, distances), not one that re-does parameter arithmetic.

## Known OpenCascade pitfalls
- Booleans can silently drop a piece. When fusing many curved pieces, use
  `fuse_robust` (common/geom.py: verifies each step, retries with the seam
  rotated) and run `check_fused` (common/checks.py) on the result.
- Spheres have a seam (+X) and poles (±Z). Keep both away from where other
  pieces touch: rotate them to hidden sides or onto a limb's axis.
- `Cone` with equal radii fails; use `Cylinder`.

## New models
Write `design.md` first and get it confirmed before writing `model.py`.
Copy the structure of `models/pill_box/`. Every model with a fit should
have a `coupon` variant: a small, fast print that tests just the fit.

## Showing the model
- `--show`: sends the model to the OCP CAD Viewer panel in VS Code (the
  viewer must be open: command palette → "OCP CAD Viewer: Open viewer").
- `out/<variant>/viewer.html`: interactive 3D in a browser (open with `open`).
- `out/<variant>/drawing_<part>.pdf`: technical drawing sheet (opens in VS Code).
- `out/<variant>/<name>_plate.3mf`: a Bambu Studio project with our P2S
  settings (`common/bambu/*.config`), so it opens ready to slice and send.
  Each run also slices it headlessly with Bambu Studio's CLI and writes the
  print time and filament to `out/<variant>/slice_estimate.json`.
  Bambu Studio may save its sliced project over this file; the next run
  overwrites it, so copy it into `prints/` first and log it in `notes.md`.

## Printer
Bambu Lab P2S, 256 × 256 × 256 mm build volume (`BED` in `common/checks.py`).
Default settings: P2S 0.4 nozzle, Generic PLA, 0.20mm Standard
(`common/bambu/p2s_pla_0.20_standard.config`, captured from a saved project;
`python -m common.bambu extract <saved.3mf> <name>` captures new ones).

## Setup
```
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```
