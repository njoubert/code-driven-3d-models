"""Send a model to the OCP CAD Viewer panel in VS Code (live, interactive).

The viewer must be open: run "OCP CAD Viewer: Open viewer" from the command
palette, or open any file that imports ocp_vscode (autostart).
"""

from __future__ import annotations

from .model import Model


def show_model(model: Model) -> bool:
    try:
        from ocp_vscode import get_port, port_check, show
        # show() only prints errors when no viewer is listening, so check first
        port = get_port()
        if port is None or not port_check(int(port)):
            raise ConnectionError("no viewer listening")
        show(*[p.shape for p in model.parts],
             names=[p.name for p in model.parts],
             colors=[p.color for p in model.parts],
             alphas=[0.6 if p.reference else 1.0 for p in model.parts],
             reset_camera="keep")
        return True
    except Exception as e:  # viewer not open, port not found, ...
        print(f"  could not reach OCP CAD Viewer ({type(e).__name__}: {e})")
        print("  open it in VS Code: Cmd-Shift-P → 'OCP CAD Viewer: Open viewer', then rerun with --show")
        return False
