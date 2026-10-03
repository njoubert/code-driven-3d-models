"""Exports: STEP (use pose, exact geometry), STL (print pose), a 3MF print
plate with every printed part laid out, and a self-contained viewer.html."""

from __future__ import annotations

import base64
import json
import re
import struct
import uuid
import zipfile
from pathlib import Path

import numpy as np
from build123d import Location, Mesher, export_step, export_stl

from .geom import TESS_ANGLE, TESS_TOL, mesh_arrays, print_shape
from .model import Model

PLATE_GAP = 10.0  # mm between parts on the print plate
# Outputs are committed, so keep them byte-stable: fixed STEP timestamp, name-derived 3MF UUIDs.
STEP_TIMESTAMP = "2000-01-01T00:00:00"


def export_all(model: Model, out: Path) -> list[Path]:
    written = []
    for part in model.printed:
        step = out / f"{part.name}.step"
        export_step(part.shape, step, timestamp=STEP_TIMESTAMP)
        stl = out / f"{part.name}.stl"
        export_stl(print_shape(part), stl, TESS_TOL, TESS_ANGLE)
        written += [step, stl]

    plate = out / f"{model.name}_plate.3mf"
    mesher = Mesher()
    for part, loc in zip(model.printed, plate_layout(model)):
        mesher.add_shape(print_shape(part).moved(loc), TESS_TOL, TESS_ANGLE, part_number=part.name)
    mesher.write(plate)
    _stable_uuids(plate, model.name)
    written.append(plate)

    viewer = out / "viewer.html"
    viewer.write_text(viewer_html(model), encoding="utf-8")
    written.append(viewer)
    return written


def _stable_uuids(path: Path, seed: str):
    """lib3mf assigns random UUIDs; replace each with one derived from the model name."""
    with zipfile.ZipFile(path) as z:
        entries = [(i.filename, z.read(i)) for i in z.infolist()]
    mapping: dict[str, str] = {}

    def sub(m):
        new = mapping.setdefault(m.group(1), str(uuid.uuid5(uuid.NAMESPACE_URL, f"{seed}/{len(mapping)}")))
        return f'UUID="{new}"'

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name, data in entries:
            if name.endswith(".model"):
                data = re.sub(r'UUID="([0-9a-fA-F-]{36})"', sub, data.decode()).encode()
            z.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), data, zipfile.ZIP_DEFLATED)


def plate_layout(model: Model) -> list[Location]:
    """Place print-pose parts side by side along X, centred on the origin."""
    widths = [print_shape(p).bounding_box().size.X for p in model.printed]
    total = sum(widths) + PLATE_GAP * (len(widths) - 1)
    x, locs = -total / 2, []
    for w in widths:
        locs.append(Location((x + w / 2, 0, 0)))
        x += w + PLATE_GAP
    return locs


def stl_bytes(shape) -> bytes:
    v, f = mesh_arrays(shape)
    tri = v[f].astype(np.float32)
    n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
    n /= np.maximum(np.linalg.norm(n, axis=1, keepdims=True), 1e-12)
    rec = np.zeros(len(f), dtype=[("n", "<f4", 3), ("v", "<f4", (3, 3)), ("a", "<u2")])
    rec["n"], rec["v"] = n, tri
    return b"\0" * 80 + struct.pack("<I", len(f)) + rec.tobytes()


def viewer_html(model: Model) -> str:
    parts = [{
        "name": p.name,
        "color": p.color,
        "explode": list(p.explode),
        "reference": p.reference,
        "stl": base64.b64encode(stl_bytes(p.shape)).decode(),
    } for p in model.parts]
    return VIEWER_TEMPLATE.replace("__TITLE__", model.title).replace("__PARTS__", json.dumps(parts))


VIEWER_TEMPLATE = """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>__TITLE__</title>
<style>
  :root { --bg:#f4f2ee; --fg:#222; --panel:#ffffffd9; --line:#0002; }
  @media (prefers-color-scheme: dark) { :root { --bg:#1d1d1f; --fg:#eee; --panel:#2a2a2dd9; --line:#fff2; } }
  html,body { margin:0; height:100%; background:var(--bg); color:var(--fg); font:14px system-ui,sans-serif; }
  #ui { position:fixed; top:12px; left:12px; background:var(--panel); border:1px solid var(--line);
        border-radius:8px; padding:10px 12px; display:grid; gap:6px; }
  #ui h1 { font-size:15px; margin:0 0 4px; }
  label { display:flex; gap:6px; align-items:center; }
  canvas { display:block; }
</style></head><body>
<div id="ui"><h1>__TITLE__</h1><div id="toggles"></div>
  <label>explode <input id="explode" type="range" min="0" max="1" step="0.01" value="0"></label>
  <label><input id="wire" type="checkbox"> edges only</label>
  <small>drag: orbit · right-drag: pan · scroll: zoom · grid = 10 mm</small></div>
<script type="importmap">{"imports":{"three":"https://cdn.jsdelivr.net/npm/three@0.170.0/build/three.module.js",
"three/addons/":"https://cdn.jsdelivr.net/npm/three@0.170.0/examples/jsm/"}}</script>
<script type="module">
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
import { STLLoader } from "three/addons/loaders/STLLoader.js";
const PARTS = __PARTS__;
THREE.Object3D.DEFAULT_UP.set(0, 0, 1);
const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true });
renderer.setPixelRatio(devicePixelRatio); document.body.appendChild(renderer.domElement);
const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(35, 1, 0.1, 5000);
const controls = new OrbitControls(camera, renderer.domElement);
scene.add(new THREE.HemisphereLight(0xffffff, 0x666666, 2.2));
const sun = new THREE.DirectionalLight(0xffffff, 1.6); sun.position.set(-1, -2, 3); scene.add(sun);
const loader = new STLLoader(), objs = [], box = new THREE.Box3();
const toggles = document.getElementById("toggles");
for (const p of PARTS) {
  const bin = Uint8Array.from(atob(p.stl), c => c.charCodeAt(0));
  const geo = loader.parse(bin.buffer);
  const mesh = new THREE.Mesh(geo, new THREE.MeshStandardMaterial({ color: p.color, roughness: 0.6, metalness: 0.05 }));
  const edges = new THREE.LineSegments(new THREE.EdgesGeometry(geo, 30), new THREE.LineBasicMaterial({ color: 0x333333 }));
  const g = new THREE.Group(); g.add(mesh, edges); scene.add(g); objs.push({ p, g, mesh });
  box.expandByObject(g);
  const l = document.createElement("label");
  l.innerHTML = `<input type="checkbox" checked> ${p.name}${p.reference ? " (reference)" : ""}`;
  l.firstChild.onchange = e => { g.visible = e.target.checked; }; toggles.appendChild(l);
}
const c = box.getCenter(new THREE.Vector3()), r = box.getSize(new THREE.Vector3()).length();
const grid = new THREE.GridHelper(Math.ceil(r / 10) * 20, Math.ceil(r / 10) * 2, 0x888888, 0xbbbbbb);
grid.rotation.x = Math.PI / 2; grid.position.set(c.x, c.y, box.min.z - 0.01); scene.add(grid);
scene.add(new THREE.AxesHelper(r * 0.25));
camera.position.set(c.x - r * 0.8, c.y - r * 1.4, c.z + r * 0.9); controls.target.copy(c); controls.update();
document.getElementById("explode").oninput = e => { for (const o of objs) o.g.position.set(...o.p.explode.map(v => v * e.target.value)); };
document.getElementById("wire").onchange = e => { for (const o of objs) o.mesh.visible = !e.target.checked; };
function resize() { renderer.setSize(innerWidth, innerHeight); camera.aspect = innerWidth / innerHeight; camera.updateProjectionMatrix(); }
addEventListener("resize", resize); resize();
renderer.setAnimationLoop(() => { controls.update(); renderer.render(scene, camera); });
</script></body></html>
"""
