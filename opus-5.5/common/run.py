"""Build → check → export → render → draw, for one model.

    .venv/bin/python -m common.run pill_box                 # everything
    .venv/bin/python -m common.run pill_box --variant coupon
    .venv/bin/python -m common.run pill_box --fast          # checks + exports only
    .venv/bin/python -m common.run pill_box --fast --show   # ... and send to OCP CAD Viewer in VS Code

Outputs go to models/<name>/out/<variant>/. Exit code 1 if any check fails.
"""

from __future__ import annotations

import argparse
import importlib
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("model")
    ap.add_argument("--variant", default="full")
    ap.add_argument("--fast", action="store_true", help="skip render sheet and drawings")
    ap.add_argument("--show", action="store_true", help="send the model to OCP CAD Viewer in VS Code")
    args = ap.parse_args()

    from .checks import run_checks
    from .export import export_all

    t0 = time.time()
    module = importlib.import_module(f"models.{args.model}.model")
    model = module.build(args.variant)
    out = ROOT / "models" / args.model / "out" / args.variant
    out.mkdir(parents=True, exist_ok=True)
    print(f"[build]   {model.title} ({args.variant}): {', '.join(p.name for p in model.parts)}"
          f"  {time.time() - t0:.1f}s")

    print("[checks]")
    report = run_checks(model)
    report.print()

    written = export_all(model, out)
    if not args.fast:
        from .drawing import draw_sheets
        from .render import render_sheet
        sheet = out / "render_sheet.png"
        render_sheet(model, sheet)
        written += [sheet] + draw_sheets(model, out)

    if args.show:
        from .show import show_model
        print("[show]    OCP CAD Viewer: " + ("sent" if show_model(model) else "not reachable"))

    print("[outputs]")
    for p in written:
        print(f"  {p.relative_to(ROOT)}")
    print(f"[done]    {time.time() - t0:.1f}s")
    sys.exit(1 if report.failed else 0)


if __name__ == "__main__":
    main()
