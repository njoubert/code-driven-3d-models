"""Bambu Studio project export and headless slicing.

`write_project` writes a Bambu Studio project 3MF: our parts as separate,
named objects on plate 1, plus print settings copied from a project you
saved in Bambu Studio. It opens with printer, filament and process already
selected (no "load geometry only" prompt).

`slice_project` runs Bambu Studio's command-line slicer on it and returns
the estimated print time and filament use.

Settings live in common/bambu/<name>.config. To capture new ones, set up a
print in Bambu Studio, save the project, then:

    .venv/bin/python -m common.bambu extract path/to/saved.3mf <name>
"""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import uuid
import zipfile
from pathlib import Path

import numpy as np

from .geom import mesh_arrays

SETTINGS_DIR = Path(__file__).parent / "bambu"
DEFAULT_SETTINGS = SETTINGS_DIR / "p2s_pla_0.20_standard.config"
BAMBU_CLI = Path("/Applications/BambuStudio.app/Contents/MacOS/BambuStudio")

NS = ('xmlns="http://schemas.microsoft.com/3dmanufacturing/core/2015/02" '
      'xmlns:BambuStudio="http://schemas.bambulab.com/package/2021" '
      'xmlns:p="http://schemas.microsoft.com/3dmanufacturing/production/2015/06" requiredextensions="p"')
IDENTITY4 = "1 0 0 0 0 1 0 0 0 0 1 0 0 0 0 1"


def write_project(path: Path, objects: list[tuple[str, object]], seed: str,
                  settings: Path = DEFAULT_SETTINGS):
    """objects: (name, shape) pairs, already placed on the bed (print pose, z=0 floor)."""
    config = settings.read_text()
    version = json.loads(config).get("version", "02.08.02.61")
    ids = lambda k: (2 * k + 1, 2 * k + 2)          # (mesh object id, wrapper object id)
    uid = lambda tag: str(uuid.uuid5(uuid.NAMESPACE_URL, f"{seed}/{tag}"))

    files: dict[str, str] = {}
    resources, items, settings_objs, instances, assemble, rels = [], [], [], [], [], []
    for k, (name, shape) in enumerate(objects):
        mesh_id, obj_id = ids(k)
        v, f = _welded(shape)
        centre = (v.min(axis=0) + v.max(axis=0)) / 2
        v = v - centre
        t = " ".join(f"{c:.6f}" for c in centre)
        part_file = f"3D/Objects/object_{k + 1}.model"

        verts = "\n".join(f'     <vertex x="{x:.5f}" y="{y:.5f}" z="{z:.5f}"/>' for x, y, z in v)
        tris = "\n".join(f'     <triangle v1="{a}" v2="{b}" v3="{c}"/>' for a, b, c in f)
        files[part_file] = (
            f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
            f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n <resources>\n'
            f'  <object id="{mesh_id}" p:UUID="{uid(f"mesh/{name}")}" type="model">\n   <mesh>\n'
            f'    <vertices>\n{verts}\n    </vertices>\n    <triangles>\n{tris}\n    </triangles>\n'
            f'   </mesh>\n  </object>\n </resources>\n <build/>\n</model>\n')

        resources.append(
            f'  <object id="{obj_id}" p:UUID="{uid(f"object/{name}")}" type="model">\n   <components>\n'
            f'    <component p:path="/{part_file}" objectid="{mesh_id}" p:UUID="{uid(f"component/{name}")}" '
            f'transform="1 0 0 0 1 0 0 0 1 0 0 0"/>\n   </components>\n  </object>')
        items.append(f'  <item objectid="{obj_id}" p:UUID="{uid(f"item/{name}")}" '
                     f'transform="1 0 0 0 1 0 0 0 1 {t}" printable="1"/>')
        rels.append(f' <Relationship Target="/{part_file}" Id="rel-{k + 1}" '
                    f'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>')
        settings_objs.append(
            f'  <object id="{obj_id}">\n    <metadata key="name" value="{name}"/>\n'
            f'    <metadata key="extruder" value="1"/>\n'
            f'    <part id="{mesh_id}" subtype="normal_part">\n      <metadata key="name" value="{name}"/>\n'
            f'      <metadata key="matrix" value="{IDENTITY4}"/>\n    </part>\n  </object>')
        instances.append(f'    <model_instance>\n      <metadata key="object_id" value="{obj_id}"/>\n'
                         f'      <metadata key="instance_id" value="0"/>\n'
                         f'      <metadata key="identify_id" value="{100 + k}"/>\n    </model_instance>')
        assemble.append(f'   <assemble_item object_id="{obj_id}" instance_id="0" '
                        f'transform="1 0 0 0 1 0 0 0 1 {t}" offset="0 0 0" />')

    files["3D/3dmodel.model"] = (
        f'<?xml version="1.0" encoding="UTF-8"?>\n<model unit="millimeter" xml:lang="en-US" {NS}>\n'
        f' <metadata name="Application">BambuStudio-{version}</metadata>\n'
        f' <metadata name="BambuStudio:3mfVersion">1</metadata>\n'
        f' <metadata name="Title">{seed}</metadata>\n'
        f' <resources>\n' + "\n".join(resources) + '\n </resources>\n'
        f' <build p:UUID="{uid("build")}">\n' + "\n".join(items) + '\n </build>\n</model>\n')
    files["3D/_rels/3dmodel.model.rels"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        + "\n".join(rels) + '\n</Relationships>\n')
    files["Metadata/model_settings.config"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n' + "\n".join(settings_objs) +
        '\n  <plate>\n    <metadata key="plater_id" value="1"/>\n    <metadata key="plater_name" value=""/>\n'
        '    <metadata key="locked" value="false"/>\n' + "\n".join(instances) + '\n  </plate>\n'
        '  <assemble>\n' + "\n".join(assemble) + '\n  </assemble>\n</config>\n')
    files["Metadata/project_settings.config"] = config
    files["Metadata/slice_info.config"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n<config>\n  <header>\n'
        '    <header_item key="X-BBL-Client-Type" value="slicer"/>\n'
        f'    <header_item key="X-BBL-Client-Version" value="{version}"/>\n  </header>\n</config>\n')
    files["_rels/.rels"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">\n'
        ' <Relationship Target="/3D/3dmodel.model" Id="rel-1" '
        'Type="http://schemas.microsoft.com/3dmanufacturing/2013/01/3dmodel"/>\n</Relationships>\n')
    files["[Content_Types].xml"] = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">\n'
        ' <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>\n'
        ' <Default Extension="model" ContentType="application/vnd.ms-package.3dmanufacturing-3dmodel+xml"/>\n'
        ' <Default Extension="png" ContentType="image/png"/>\n'
        ' <Default Extension="gcode" ContentType="text/x.gcode"/>\n</Types>\n')

    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        for name in sorted(files):     # fixed order + fixed timestamps: byte-stable for git
            z.writestr(zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0)), files[name], zipfile.ZIP_DEFLATED)


def _welded(shape) -> tuple[np.ndarray, np.ndarray]:
    """Mesh with coincident vertices merged, so slicers see a closed (manifold) surface."""
    v, f = mesh_arrays(shape)
    keys = np.round(v, 5)
    uniq, inverse = np.unique(keys, axis=0, return_inverse=True)
    f = inverse.reshape(-1)[f]
    f = f[(f[:, 0] != f[:, 1]) & (f[:, 1] != f[:, 2]) & (f[:, 0] != f[:, 2])]
    return uniq, f


def slice_project(path: Path) -> dict | None:
    """Slice plate 1 with Bambu Studio's CLI -> {"minutes", "grams", ...}, or None if unavailable."""
    if not BAMBU_CLI.exists():
        return None
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run([str(BAMBU_CLI), "--slice", "0", "--debug", "1", "--outputdir", tmp, str(path)],
                       capture_output=True, timeout=600, cwd=tmp)  # it also drops a result.json in cwd
        result = Path(tmp) / "result.json"
        if not result.exists():
            return {"error": "Bambu Studio produced no result.json"}
        r = json.loads(result.read_text())
    if r.get("return_code") != 0:
        return {"error": r.get("error_string", "slicing failed")}
    plate = r["sliced_plates"][0]
    return {
        "minutes": round(plate["main_predication"] / 60, 1),
        "grams": round(sum(f["total_used_g"] for f in plate["filaments"]), 2),
        "layer_height": round(r["layer_height"], 2),
    }


if __name__ == "__main__":
    if len(sys.argv) == 4 and sys.argv[1] == "extract":
        src, name = Path(sys.argv[2]), sys.argv[3]
        with zipfile.ZipFile(src) as z:
            config = z.read("Metadata/project_settings.config").decode()
        dest = SETTINGS_DIR / f"{name}.config"
        dest.write_text(config)
        c = json.loads(config)
        print(f"wrote {dest}: {c['printer_settings_id']} | {c['print_settings_id']} | {c['filament_settings_id']}")
    else:
        print(__doc__)
