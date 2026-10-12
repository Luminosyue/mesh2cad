#!/usr/bin/env python3
"""CASE09 PhysX grounded views: shaded whole-object cameras + per-P3-part prompts.

Writes a new directory. Does not overwrite the frozen PhysX audit.
Object orientation is frozen; only the camera orbits.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad/ours3")
OUT = ROOT / "case09_aircraft_end2end_cad_v1"
SOURCE = ROOT / "meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"
P3 = OUT / "01_part_discovery/p3"
DEST = OUT / "01_part_discovery/physx_grounded"
VIEWS = ("isometric", "side", "top")
MAX_FACES = 120000

sys.path.insert(0, str(ROOT / "fusion_pipeline/scripts"))
from render_obj_for_physx import (  # noqa: E402
    CAMERAS,
    FACE_RGB,
    GHOST_RGB,
    PART_RGB,
    draw_shaded_layers,
    load_mesh,
    normalization,
    protocol_for,
    view_png,
)


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, default=str) + "\n", encoding="utf-8")


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def extract_part(source, labels, part_id):
    ids = np.flatnonzero(labels == part_id)
    faces = np.asarray(source.faces)[ids]
    vertices, inverse = np.unique(faces.reshape(-1), return_inverse=True)
    return (
        trimesh.Trimesh(
            vertices=np.asarray(source.vertices)[vertices],
            faces=inverse.reshape(-1, 3),
            process=False,
        ),
        ids,
    )


def contact_sheet(paths: list[Path], titles: list[str], output: Path, cols: int = 4) -> None:
    rows = int(np.ceil(len(paths) / cols))
    figure, axes = plt.subplots(rows, cols, figsize=(3.2 * cols, 3.2 * rows), dpi=110, facecolor="white")
    axes = np.atleast_1d(axes).ravel()
    for axis, path, title in zip(axes, paths, titles):
        image = np.asarray(Image.open(path).convert("RGB"))
        axis.imshow(image)
        axis.set_title(title, fontsize=8)
        axis.axis("off")
    for axis in axes[len(paths) :]:
        axis.axis("off")
    figure.tight_layout(pad=0.3)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, facecolor="white")
    plt.close(figure)


def main() -> int:
    source = load_mesh(SOURCE)
    normalized, transform = normalization(source)
    labels = np.load(P3 / "triangle_part_id.npy", allow_pickle=False)
    metadata = load(P3 / "part_metadata.json")
    if len(labels) != len(normalized.faces):
        raise RuntimeError(f"P3 labels {len(labels)} != source triangles {len(normalized.faces)}")
    bounds = np.asarray(normalized.bounds, dtype=float)
    input_dir = DEST / "input"
    part_dir = DEST / "parts"
    input_dir.mkdir(parents=True, exist_ok=True)
    part_dir.mkdir(parents=True, exist_ok=True)

    whole_png = input_dir / "CASE09_shaded.png"
    whole_images = {}
    for view in VIEWS:
        path = view_png(whole_png, view)
        draw_shaded_layers(
            [{"mesh": normalized, "rgb": FACE_RGB, "max_faces": MAX_FACES, "alpha": 1.0}],
            bounds,
            CAMERAS[view],
            path,
        )
        whole_images[view] = str(path)

    parts = []
    sheet_paths = [Path(whole_images[view]) for view in VIEWS]
    sheet_titles = [f"whole {view}" for view in VIEWS]
    for row in sorted(metadata["parts"], key=lambda item: int(item["part_id"])):
        part_id = int(row["part_id"])
        part_mesh, ids = extract_part(normalized, labels, part_id)
        close_path = part_dir / f"part_{part_id:03d}_closeup.png"
        context_path = part_dir / f"part_{part_id:03d}_context.png"
        draw_shaded_layers(
            [{"mesh": part_mesh, "rgb": PART_RGB, "max_faces": MAX_FACES, "alpha": 1.0}],
            np.asarray(part_mesh.bounds, dtype=float),
            CAMERAS["isometric"],
            close_path,
        )
        draw_shaded_layers(
            [
                {"mesh": normalized, "rgb": GHOST_RGB, "max_faces": MAX_FACES, "alpha": 0.22},
                {"mesh": part_mesh, "rgb": PART_RGB, "max_faces": MAX_FACES, "alpha": 1.0},
            ],
            bounds,
            CAMERAS["isometric"],
            context_path,
        )
        record = {
            "p3_part_id": part_id,
            "triangle_count": int(len(ids)),
            "bbox": np.asarray(part_mesh.bounds).tolist(),
            "closeup": str(close_path),
            "context": str(context_path),
            "prompt_images": [whole_images["isometric"], str(context_path), str(close_path)],
        }
        parts.append(record)
        sheet_paths.extend([context_path, close_path])
        sheet_titles.extend([f"P3 {part_id:03d} context", f"P3 {part_id:03d} close-up"])

    contact = DEST / "artifacts/grounded_contact_sheet.png"
    contact_sheet(sheet_paths, sheet_titles, contact, cols=4)
    payload = {
        "schema": "CASE09_PHYSX_GROUNDED_VIEWS_V1",
        "source_obj": str(SOURCE),
        "p3_labels": str(P3 / "triangle_part_id.npy"),
        "object_rotation": "NONE",
        "semantic_prior_is_soft": True,
        "physical_scale_used_as_hard_constraint": False,
        "protocol": protocol_for(list(VIEWS), shaded=True, max_faces=MAX_FACES),
        "normalization_transform": transform,
        "whole_object": whole_images,
        "parts": parts,
        "contact_sheet": str(contact),
        "whole_object_prompt_images": [whole_images[view] for view in VIEWS],
    }
    dump(DEST / "input/render_metadata.json", payload)
    dump(DEST / "artifacts/view_manifest.json", payload)
    print(json.dumps({"DEST": str(DEST), "WHOLE_VIEWS": list(VIEWS), "P3_PARTS": len(parts), "CONTACT": str(contact)}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
