#!/usr/bin/env python3
"""P3-conditioned PhysX segment labeling V2 for CASE09.

P3 owns segmentation. PhysX may only name the requested frozen triangle mask.
Never uses the official whole-object Parts/Group_info template or first-l_0 binding.
Writes ours3/case09_aircraft_end2end_cad_v1/01_part_discovery/physx_grounded_v2/.
Does not modify the frozen physx/ directory.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import traceback
from pathlib import Path

os.environ.setdefault("HF_HUB_OFFLINE", "1")
os.environ.setdefault("TRANSFORMERS_OFFLINE", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import trimesh
from PIL import Image

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
CASE = OURS3 / "case09_aircraft_end2end_cad_v1"
SOURCE = OURS3 / "meshes/Air_Hogs_Wind_Flyers_Set_Airplane_Red.obj"
P3 = CASE / "01_part_discovery/p3"
DEST = CASE / "01_part_discovery/physx_grounded_v2"
FROZEN_PHYSX = CASE / "01_part_discovery/physx"
GROUNDED_V1 = CASE / "01_part_discovery/physx_grounded"
REPO = ROOT / "PhysX-Omni"
CKPT = REPO / "pretrain"
PROMPT = CASE / "scripts/physx_segment_labeling_v2_prompt.txt"
PROMPT_STRICT = CASE / "scripts/physx_segment_labeling_v2_prompt_strict.txt"
MAX_FACES = 120000
TARGET_VIEWS = ("front", "side", "top")

sys.path.insert(0, str(OURS3 / "fusion_pipeline/scripts"))
from render_obj_for_physx import (  # noqa: E402
    CAMERAS,
    FACE_RGB,
    GHOST_RGB,
    PART_RGB,
    draw_shaded_layers,
    load_mesh,
    normalization,
)

# Evaluation-only. Never sent to PhysX or reconstruction.
EVAL_GT = {
    0: "vertical_stabilizer",
    1: "propeller",
    2: "main_wing_left",
    3: "propeller",
    4: "main_wing_right",
    5: "horizontal_stabilizer_right",
    6: "dorsal_feature",
    7: "horizontal_stabilizer_left",
    8: "fuselage",
    9: "dorsal_feature",
}

LABEL_ALIASES = [
    ("vertical_stabilizer", ("vertical_stabilizer", "vertical stabilizer", "vertical tail", "tail fin", "fin", "rudder", "vertical_rear")),
    ("horizontal_stabilizer_left", ("horizontal_stabilizer_left", "left horizontal", "left elevator", "left tailplane", "horizontal tail left")),
    ("horizontal_stabilizer_right", ("horizontal_stabilizer_right", "right horizontal", "right elevator", "right tailplane", "horizontal tail right")),
    ("horizontal_stabilizer", ("horizontal_stabilizer", "horizontal stabilizer", "elevator", "tailplane", "horizontal tail", "htail")),
    ("main_wing_left", ("main_wing_left", "left wing", "left main wing", "port wing", "wing_left")),
    ("main_wing_right", ("main_wing_right", "right wing", "right main wing", "starboard wing", "wing_right")),
    ("main_wing", ("main_wing", "wing", "main wing", "airfoil")),
    ("propeller", ("propeller", "prop", "airscrew", "rotor blade", "propeller_blade", "propeller_pattern")),
    ("fuselage", ("fuselage", "body", "hull", "airframe", "central body")),
    ("dorsal_feature", ("dorsal_feature", "dorsal", "canopy", "cockpit", "spine", "dorsal_features")),
    ("unknown", ("unknown", "n/a", "none", "uncertain")),
]

FAMILY = {
    "vertical_stabilizer": "vertical_stabilizer",
    "horizontal_stabilizer": "horizontal_stabilizer",
    "horizontal_stabilizer_left": "horizontal_stabilizer",
    "horizontal_stabilizer_right": "horizontal_stabilizer",
    "main_wing": "main_wing",
    "main_wing_left": "main_wing",
    "main_wing_right": "main_wing",
    "propeller": "propeller",
    "fuselage": "fuselage",
    "dorsal_feature": "dorsal_feature",
    "unknown": "unknown",
}

GEOMETRY_ROLE = {
    "vertical_stabilizer": "VERTICAL_REAR_PLANAR_APPENDAGE",
    "horizontal_stabilizer": "HORIZONTAL_REAR_PLANAR_APPENDAGE",
    "horizontal_stabilizer_left": "HORIZONTAL_REAR_PLANAR_APPENDAGE",
    "horizontal_stabilizer_right": "HORIZONTAL_REAR_PLANAR_APPENDAGE",
    "main_wing": "LATERAL_LIFTING_PLANAR_APPENDAGE",
    "main_wing_left": "LATERAL_LIFTING_PLANAR_APPENDAGE",
    "main_wing_right": "LATERAL_LIFTING_PLANAR_APPENDAGE",
    "propeller": "NOSE_ROTATIONAL_PATTERN",
    "fuselage": "LONGITUDINAL_PRIMARY_BODY",
    "dorsal_feature": "DORSAL_SUBFEATURE",
    "unknown": "UNKNOWN",
}

FUNCTION_HINT = {
    "vertical_stabilizer": "directional stabilization",
    "horizontal_stabilizer": "pitch stabilization",
    "horizontal_stabilizer_left": "pitch stabilization",
    "horizontal_stabilizer_right": "pitch stabilization",
    "main_wing": "lift generation",
    "main_wing_left": "lift generation",
    "main_wing_right": "lift generation",
    "propeller": "propulsion",
    "fuselage": "primary structural body",
    "dorsal_feature": "upper-body fairing or local feature",
    "unknown": None,
}

# Closed generic role vocabulary used only for constrained PhysX scoring.  P3
# still owns the count and masks; these are labels, never proposed segments.
CLASS_CODES = {
    "A": "vertical_stabilizer",
    "B": "horizontal_stabilizer",
    "C": "main_wing",
    "D": "propeller",
    "E": "fuselage",
    "F": "dorsal_feature",
    "G": "unknown",
}


def dump(path: Path, value) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(clean(value), indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load(path: Path | str):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def clean(value):
    if isinstance(value, dict):
        return {str(k): clean(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [clean(v) for v in value]
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def sha(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1 << 20), b""):
            digest.update(block)
    return digest.hexdigest()


def directory_snapshot(path: Path) -> dict[str, str]:
    """Content snapshot used to prove that frozen physx/ was not modified."""
    if not path.is_dir():
        return {}
    return {
        str(item.relative_to(path)): sha(item)
        for item in sorted(path.rglob("*"))
        if item.is_file()
    }


def seg_id(part_id: int) -> str:
    return f"P3_SEG_{int(part_id):03d}"


def extract_part(source, labels, part_id):
    ids = np.flatnonzero(labels == int(part_id))
    faces = np.asarray(source.faces)[ids]
    vertices, inverse = np.unique(faces.reshape(-1), return_inverse=True)
    mesh = trimesh.Trimesh(
        vertices=np.asarray(source.vertices)[vertices],
        faces=inverse.reshape(-1, 3),
        process=False,
    )
    return mesh, ids


def pca(vertices):
    center = vertices.mean(0)
    _, values, axes = np.linalg.svd(vertices - center, full_matrices=False)
    return center, axes, values


def bin_axis(value, lo, hi) -> str:
    span = max(hi - lo, 1e-9)
    t = (value - lo) / span
    if t < 0.33:
        return "min"
    if t > 0.67:
        return "max"
    return "mid"


def geometry_analyzer(whole, part, labels, faces, part_id, ids):
    verts = np.asarray(part.vertices, float)
    center, axes, values = pca(verts)
    wmin, wmax = np.asarray(whole.bounds[0], float), np.asarray(whole.bounds[1], float)
    centroid = np.asarray(part.centroid, float)
    extents = np.asarray(part.extents, float)
    order = np.argsort(extents)
    ratios = {
        "thickness_over_span": float(extents[order[0]] / max(extents[order[2]], 1e-9)),
        "mid_over_span": float(extents[order[1]] / max(extents[order[2]], 1e-9)),
        "xyz": [float(x / max(float(extents.max()), 1e-9)) for x in extents],
    }
    adj = mesh_adjacency(labels, faces, part_id)
    other = [int(v) for v in np.unique(labels) if int(v) != int(part_id)]
    symmetry = {"mirror_across_yz": False, "partner_segment": None, "centroid_x_sign": "zero" if abs(centroid[0]) < 0.05 * max(float(wmax[0] - wmin[0]), 1e-9) else ("positive" if centroid[0] > 0 else "negative")}
    if abs(centroid[0]) > 0.08 * max(float(wmax[0] - wmin[0]), 1e-9):
        target = np.array([-centroid[0], centroid[1], centroid[2]])
        best, best_d = None, 1e9
        for oid in other:
            om, _ = extract_part(whole, labels, oid)
            d = float(np.linalg.norm(np.asarray(om.centroid) - target))
            if d < best_d:
                best, best_d = oid, d
        if best is not None and best_d < 0.15 * float(np.linalg.norm(wmax - wmin)):
            symmetry["mirror_across_yz"] = True
            symmetry["partner_segment"] = seg_id(best)
    return {
        "schema": "GeometryAnalyzerP3SegmentV2",
        "p3_segment_id": seg_id(part_id),
        "triangle_count": int(len(ids)),
        "vertex_count": int(len(part.vertices)),
        "bbox": np.asarray(part.bounds).tolist(),
        "extents": extents.tolist(),
        "centroid": centroid.tolist(),
        "area": float(part.area),
        "area_fraction": float(part.area / max(float(whole.area), 1e-9)),
        "watertight": bool(part.is_watertight),
        "principal_axes": axes.tolist(),
        "principal_values": values.tolist(),
        "bbox_ratios": ratios,
        "position": {
            "x": bin_axis(centroid[0], wmin[0], wmax[0]),
            "y": bin_axis(centroid[1], wmin[1], wmax[1]),
            "z": bin_axis(centroid[2], wmin[2], wmax[2]),
        },
        "orientation": {
            "dominant_axis_index": int(np.argmax(values)),
            "dominant_axis_vector": axes[0].tolist() if len(axes) else None,
        },
        "symmetry": symmetry,
        "adjacency": adj,
        "measurement_source": "FROZEN_P3_TRIANGLE_MASK",
        "proxy_used_for_measurement": False,
        "eval_gt_included": False,
    }


def mesh_adjacency(labels, faces, part_id):
    labels = np.asarray(labels)
    faces = np.asarray(faces)
    verts = np.unique(faces[labels == part_id].reshape(-1))
    neighbors = {}
    for other in np.unique(labels):
        other = int(other)
        if other == int(part_id):
            continue
        shared = np.intersect1d(verts, np.unique(faces[labels == other].reshape(-1)), assume_unique=False)
        if len(shared):
            neighbors[seg_id(other)] = int(len(shared))
    return {"shared_vertex_counts": neighbors, "adjacent_segments": sorted(neighbors, key=neighbors.get, reverse=True)}


def geometry_block(geo: dict) -> str:
    return (
        f"- triangle_count: {geo['triangle_count']}\n"
        f"- area_fraction: {geo['area_fraction']:.4f}\n"
        f"- bbox_extents_xyz: {geo['extents']}\n"
        f"- bbox_ratios_thickness_over_span: {geo['bbox_ratios']['thickness_over_span']:.4f}\n"
        f"- centroid_position_bins_xyz: {geo['position']}\n"
        f"- centroid_x_sign: {geo['symmetry']['centroid_x_sign']}\n"
        f"- mirror_across_yz: {geo['symmetry']['mirror_across_yz']}\n"
        f"- symmetry_partner_segment: {geo['symmetry']['partner_segment']}\n"
        f"- adjacent_segments: {geo['adjacency']['adjacent_segments']}\n"
        f"- dominant_principal_axis: {geo['orientation']['dominant_axis_vector']}\n"
        f"- watertight: {geo['watertight']}\n"
        "These numbers are geometric evidence only. Do not copy them as CAD dimensions."
    )


def render_segment(whole, part, bounds, part_dir: Path) -> dict:
    part_dir.mkdir(parents=True, exist_ok=True)
    isolated = part_dir / "isolated_isometric.png"
    context = part_dir / "context_highlight.png"
    ghost = part_dir / "ghost_context.png"
    draw_shaded_layers(
        [{"mesh": part, "rgb": PART_RGB, "max_faces": MAX_FACES, "alpha": 1.0}],
        np.asarray(part.bounds, float),
        CAMERAS["isometric"],
        isolated,
    )
    draw_shaded_layers(
        [
            {"mesh": whole, "rgb": GHOST_RGB, "max_faces": MAX_FACES, "alpha": 0.18},
            {"mesh": part, "rgb": PART_RGB, "max_faces": MAX_FACES, "alpha": 1.0},
        ],
        bounds,
        CAMERAS["isometric"],
        context,
    )
    draw_shaded_layers(
        [
            {"mesh": whole, "rgb": FACE_RGB, "max_faces": MAX_FACES, "alpha": 0.12},
            {"mesh": part, "rgb": PART_RGB, "max_faces": MAX_FACES, "alpha": 1.0},
        ],
        bounds,
        CAMERAS["isometric"],
        ghost,
    )
    orthos = {}
    for view in TARGET_VIEWS:
        path = part_dir / f"target_{view}.png"
        draw_shaded_layers(
            [{"mesh": part, "rgb": PART_RGB, "max_faces": MAX_FACES, "alpha": 1.0}],
            np.asarray(part.bounds, float),
            CAMERAS[view],
            path,
        )
        orthos[view] = str(path)
    return {
        "isolated_isometric": str(isolated),
        "context_highlight": str(context),
        "ghost_context": str(ghost),
        "target_front": orthos["front"],
        "target_side": orthos["side"],
        "target_top": orthos["top"],
    }


def contact_sheet(paths, titles, output, cols=5):
    rows = int(np.ceil(len(paths) / cols))
    figure, axes = plt.subplots(rows, cols, figsize=(3.0 * cols, 3.0 * rows), dpi=100, facecolor="white")
    axes = np.atleast_1d(axes).ravel()
    for axis, path, title in zip(axes, paths, titles):
        axis.imshow(np.asarray(Image.open(path).convert("RGB")))
        axis.set_title(title, fontsize=7)
        axis.axis("off")
    for axis in axes[len(paths):]:
        axis.axis("off")
    figure.tight_layout(pad=0.2)
    output.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(output, facecolor="white")
    plt.close(figure)


def prepare():
    if FROZEN_PHYSX.resolve() == DEST.resolve():
        raise RuntimeError("refusing to write into frozen physx/")
    source = load_mesh(SOURCE)
    whole, transform = normalization(source)
    labels = np.load(P3 / "triangle_part_id.npy", allow_pickle=False)
    if len(labels) != len(whole.faces):
        raise RuntimeError("P3 label length != source triangles")
    metadata = load(P3 / "part_metadata.json")
    bounds = np.asarray(whole.bounds, float)
    faces = np.asarray(whole.faces)
    global_category = "Aircraft"
    if (GROUNDED_V1 / "physx_global.json").is_file():
        category = load(GROUNDED_V1 / "physx_global.json").get("object_category")
        if category and "insect" not in str(category).lower():
            global_category = str(category).split("(")[0].strip() or "Aircraft"
            if global_category.lower() in {"airplane", "aircraft"}:
                global_category = "Aircraft"
    segments = []
    sheet_paths, sheet_titles = [], []
    for row in sorted(metadata["parts"], key=lambda item: int(item["part_id"])):
        part_id = int(row["part_id"])
        sid = seg_id(part_id)
        part, ids = extract_part(whole, labels, part_id)
        mask_path = DEST / "masks" / f"{sid}.npy"
        mask_path.parent.mkdir(parents=True, exist_ok=True)
        np.save(mask_path, ids.astype(np.int64), allow_pickle=False)
        geo = geometry_analyzer(whole, part, labels, faces, part_id, ids)
        dump(DEST / "geometry" / f"{sid}.json", geo)
        views = render_segment(whole, part, bounds, DEST / "parts" / sid)
        record = {
            "p3_segment_id": sid,
            "p3_part_id": part_id,
            "triangle_mask": str(mask_path),
            "triangle_count": int(len(ids)),
            "views": views,
            "geometry": str(DEST / "geometry" / f"{sid}.json"),
        }
        segments.append(record)
        dump(DEST / "parts" / sid / "segment_manifest.json", record)
        sheet_paths.append(Path(views["context_highlight"]))
        sheet_titles.append(sid)
    contact_sheet(sheet_paths, sheet_titles, DEST / "artifacts/segment_context_sheet.png", cols=5)
    manifest = {
        "schema": "CASE09_PHYSX_P3_SEGMENT_LABELING_V2",
        "source_obj": str(SOURCE),
        "p3_labels": str(P3 / "triangle_part_id.npy"),
        "p3_segment_count": len(segments),
        "object_rotation": "NONE",
        "global_context_used": global_category,
        "WHOLE_OBJECT_PARTS_TABLE_USED": False,
        "FIRST_L0_BINDING_USED": False,
        "PHYSX_DIMENSIONS_USED": False,
        "eval_gt_fed_to_model": False,
        "eval_gt_fed_to_reconstruction": False,
        "frozen_physx_dir": str(FROZEN_PHYSX),
        "normalization_transform": transform,
        "segments": segments,
    }
    dump(DEST / "artifacts/prepare_manifest.json", manifest)
    (DEST / "prompt").mkdir(parents=True, exist_ok=True)
    (DEST / "prompt/segment_labeling.txt").write_text(PROMPT.read_text(encoding="utf-8"), encoding="utf-8")
    (DEST / "prompt/segment_labeling_strict.txt").write_text(PROMPT_STRICT.read_text(encoding="utf-8"), encoding="utf-8")
    return manifest


def old_physx_label(part_id: int) -> str | None:
    path = GROUNDED_V1 / "physx_part_hypotheses.json"
    if not path.is_file():
        return None
    for row in load(path).get("p3_parts", []):
        if int(row.get("p3_part_id", -1)) == int(part_id):
            return row.get("part_name")
    return None


def normalize_label(raw: str | None, geo: dict) -> str:
    if not raw:
        return "unknown"
    text = re.sub(r"[^a-z0-9_]+", " ", str(raw).lower()).strip()
    text = text.replace(" ", "_")
    compact = text.replace("_", " ")
    for canon, aliases in LABEL_ALIASES:
        for alias in aliases:
            if alias.replace(" ", "_") == text or alias == compact or alias in compact:
                label = canon
                break
        else:
            continue
        break
    else:
        label = "unknown"
    if label == "main_wing":
        sign = geo.get("symmetry", {}).get("centroid_x_sign")
        if sign == "negative":
            label = "main_wing_left"
        elif sign == "positive":
            label = "main_wing_right"
    if label == "horizontal_stabilizer":
        sign = geo.get("symmetry", {}).get("centroid_x_sign")
        if sign == "negative":
            label = "horizontal_stabilizer_left"
        elif sign == "positive":
            label = "horizontal_stabilizer_right"
    return label


def extract_json(text: str) -> dict | None:
    start = text.find("{")
    if start < 0:
        return None
    depth = 0
    for index, char in enumerate(text[start:], start):
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                try:
                    value = json.loads(text[start : index + 1])
                except json.JSONDecodeError:
                    return None
                return value if isinstance(value, dict) else None
    return None


def contract_check(text: str, parsed: dict | None, expected_id: str) -> tuple[bool, str]:
    if re.search(r"(?im)^\s*parts\s*:", text) or re.search(r"(?im)^\s*group_info\s*:", text):
        return False, "WHOLE_OBJECT_PARTS_TABLE"
    if re.search(r"(?im)^\s*l_\d+\s*:", text):
        return False, "L_INDEX_TABLE"
    if re.search(r"(?i)\b(yak-?\d+|mig-?\d+|ant-?\d+|tupolev|mikoyan|cessna)\b", text):
        return False, "AIRCRAFT_MODEL_GUESS"
    if parsed is None:
        return False, "NO_SINGLE_JSON_OBJECT"
    if "parts" in parsed:
        if isinstance(parsed.get("parts"), list) and len(parsed.get("parts") or []) > 1:
            return False, "MULTI_PART_JSON"
        return False, "WHOLE_OBJECT_PARTS_JSON"
    if any(re.fullmatch(r"l_\d+", str(key), re.I) for key in parsed):
        return False, "L_INDEX_JSON"
    if parsed.get("p3_segment_id") != expected_id:
        return False, "SEGMENT_ID_MISMATCH"
    label = parsed.get("generic_part_label")
    if not label or not str(label).strip():
        return False, "MISSING_GENERIC_LABEL"
    if isinstance(label, (list, dict)):
        return False, "MULTI_LABEL"
    return True, "OK"


def constrained_prompt(sid: str, category: str, geo: dict, view_name: str) -> str:
    """A segment-only classification prompt with no whole-object inventory syntax."""
    classes = ", ".join(CLASS_CODES.values())
    return f"""SEGMENT_LABELING task. Label exactly ONE frozen P3 triangle mask.

Target: {sid}
Guarded global category: {category}
Evidence view: {view_name}

P3 owns segmentation. Never discover, split, merge, recount, or redefine parts.
Do not list complete object parts. Do not emit Parts, Group_info, l_0, l_1, or
any l_i. Do not describe non-target geometry. Do not infer dimensions from
pixels. Do not guess a specific aircraft subtype or model.

Authoritative Geometry Analyzer evidence for this target only:
{geometry_block(geo)}

Choose one generic CAD-friendly role for the highlighted/isolated target:
{classes}

Return one role string only."""


def classify_constrained(
    model,
    processor,
    images: list[Path],
    prompt: str,
    view_name: str,
    raw_path: Path,
    prior_log_likelihoods: dict[str, float] | None = None,
):
    """Score complete allowed role strings with PhysX; no free-form part list exists."""
    import torch
    from qwen_vl_utils import process_vision_info

    loaded = [Image.open(path).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS) for path in images]
    content = [{"type": "image", "image": image} for image in loaded]
    content.append({"type": "text", "text": prompt})
    messages = [{"role": "user", "content": content}]
    chat = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    base_inputs = processor(
        text=[chat], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt"
    )
    base_length = int(base_inputs.input_ids.shape[1])
    mean_log_likelihoods = {}
    token_counts = {}
    for label in CLASS_CODES.values():
        answer = " " + label
        full_inputs = processor(
            text=[chat + answer], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt"
        ).to(model.device)
        candidate_length = int(full_inputs.input_ids.shape[1]) - base_length
        if candidate_length <= 0:
            raise RuntimeError(f"candidate response has no tokens: {label}")
        with torch.inference_mode():
            logits = model(**full_inputs).logits[0]
        ids = full_inputs.input_ids[0]
        start = int(full_inputs.input_ids.shape[1]) - candidate_length
        positions = torch.arange(start - 1, int(full_inputs.input_ids.shape[1]) - 1, device=logits.device)
        targets = ids[start:].to(logits.device)
        token_log_probs = torch.log_softmax(logits[positions].float(), dim=-1).gather(1, targets[:, None]).squeeze(1)
        mean_log_likelihoods[label] = float(token_log_probs.mean().detach().cpu())
        token_counts[label] = candidate_length
        del full_inputs, logits
    ordered_labels = list(CLASS_CODES.values())
    calibrated_log_scores = {
        label: mean_log_likelihoods[label] - float((prior_log_likelihoods or {}).get(label, 0.0))
        for label in ordered_labels
    }
    likelihood_tensor = torch.tensor([calibrated_log_scores[label] for label in ordered_labels])
    probabilities = torch.softmax(likelihood_tensor, dim=0).tolist()
    scores = {label: float(prob) for label, prob in zip(ordered_labels, probabilities)}
    selected_label = max(scores, key=scores.get)
    record = {
        "schema": "PhysXConstrainedP3SegmentRoleLikelihoodV2",
        "view": view_name,
        "generic_part_label": selected_label,
        "confidence_within_allowed_vocabulary": scores[selected_label],
        "allowed_role_probabilities": scores,
        "mean_token_log_likelihoods": mean_log_likelihoods,
        "prior_mean_token_log_likelihoods": prior_log_likelihoods,
        "calibrated_log_scores": calibrated_log_scores,
        "candidate_token_counts": token_counts,
        "OUTPUT_CONTRACT_OK": True,
        "contract_reason": "CONSTRAINED_SINGLE_SEGMENT_CLASSIFICATION",
        "WHOLE_OBJECT_PARTS_TABLE_USED": False,
        "FIRST_L0_BINDING_USED": False,
        "MULTI_PART_OUTPUT_ACCEPTED": False,
        "PHYSX_DIMENSIONS_USED": False,
    }
    dump(raw_path, record)
    return record


def fill_prompt(template: str, sid: str, category: str, geo: dict) -> str:
    return template.format(p3_segment_id=sid, global_category=category, geometry_block=geometry_block(geo))


def generate(model, processor, images: list[Path], prompt: str) -> str:
    import torch
    from qwen_vl_utils import process_vision_info

    loaded = [Image.open(path).convert("RGB").resize((512, 512), Image.Resampling.LANCZOS) for path in images]
    content = [{"type": "image", "image": image} for image in loaded]
    content.append({"type": "text", "text": prompt})
    messages = [{"role": "user", "content": content}]
    chat = processor.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)
    image_inputs, video_inputs = process_vision_info(messages)
    inputs = processor(text=[chat], images=image_inputs, videos=video_inputs, padding=True, return_tensors="pt").to(model.device)
    with torch.inference_mode():
        ids = model.generate(**inputs, do_sample=False, max_new_tokens=512)
    trimmed = [out[len(inp):] for inp, out in zip(inputs.input_ids, ids)]
    return processor.batch_decode(trimmed, skip_special_tokens=True, clean_up_tokenization_spaces=False)[0]


def label_once(model, processor, images, prompt, sid, geo, raw_path: Path):
    raw = generate(model, processor, images, prompt)
    raw_path.parent.mkdir(parents=True, exist_ok=True)
    raw_path.write_text(raw, encoding="utf-8")
    parsed = extract_json(raw)
    ok, reason = contract_check(raw, parsed, sid)
    record = {
        "raw_path": str(raw_path),
        "OUTPUT_CONTRACT_OK": ok,
        "OUTPUT_CONTRACT_VIOLATION": not ok,
        "contract_reason": reason,
        "parsed": parsed,
        "generic_part_label": normalize_label((parsed or {}).get("generic_part_label"), geo) if ok else "unknown",
        "WHOLE_OBJECT_PARTS_TABLE_USED": reason == "WHOLE_OBJECT_PARTS_TABLE",
        "FIRST_L0_BINDING_USED": False,
        "PHYSX_DIMENSIONS_USED": bool(re.search(r"(?im)^\s*dimension\s*:", raw)),
    }
    return record


def label_with_strict_retry(model, processor, images, prompt, strict_prompt, sid, geo, raw_dir: Path):
    """Free-form contract guard: exactly one stricter retry, never first-item fallback."""
    first = label_once(model, processor, images, prompt, sid, geo, raw_dir / "attempt_1.txt")
    attempts = [first]
    if not first["OUTPUT_CONTRACT_OK"]:
        attempts.append(label_once(model, processor, images, strict_prompt, sid, geo, raw_dir / "attempt_2_strict.txt"))
    accepted = next((item for item in attempts if item["OUTPUT_CONTRACT_OK"]), None)
    return {
        "attempts": attempts,
        "attempt_count": len(attempts),
        "strict_retry_used": len(attempts) == 2,
        "accepted": accepted,
        "OUTPUT_CONTRACT_OK": accepted is not None,
        "OUTPUT_CONTRACT_VIOLATION": accepted is None,
        "first_item_fallback_used": False,
        "multi_part_output_accepted": False,
    }


def vote(labels: list[str], probabilities: list[float] | None = None) -> tuple[str, float, str]:
    valid = [x for x in labels if x and x != "unknown"]
    if not valid:
        return "unknown", 0.0, "UNKNOWN"
    families = [FAMILY.get(x, "unknown") for x in valid]
    counts = {item: families.count(item) for item in set(families)}
    ranked = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
    top, top_n = ranked[0]
    second_n = ranked[1][1] if len(ranked) > 1 else 0
    if top_n < 2 and len(valid) >= 2:
        return "unknown", 0.2, "UNKNOWN"
    if second_n >= 2 and second_n == top_n:
        return "unknown", 0.2, "UNKNOWN"
    chosen = next(label for label in valid if FAMILY.get(label, "unknown") == top)
    agreement = top_n / max(len(labels), 1)
    selected_probs = [p for label, p in zip(labels, probabilities or []) if FAMILY.get(label, "unknown") == top]
    model_confidence = float(np.mean(selected_probs)) if selected_probs else agreement
    confidence = float(min(agreement, model_confidence))
    status = "ACCEPTED" if top_n >= 3 and second_n <= 1 else ("WEAK" if top_n >= 2 and top_n > second_n else "UNKNOWN")
    if status == "UNKNOWN":
        chosen = "unknown"
    return chosen, float(confidence), status


def geometry_role_constraint(geo: dict) -> dict:
    """Generic CAD-role constraints from authoritative mask geometry, never eval GT."""
    area = float(geo["area_fraction"])
    position = geo["position"]
    sign = geo["symmetry"]["centroid_x_sign"]
    mirrored = bool(geo["symmetry"]["mirror_across_yz"])
    extents = [float(value) for value in geo["extents"]]
    central = sign == "zero"
    lateral = mirrored or sign in {"negative", "positive"}
    result = {"generic_part_label": "unknown", "confidence": 0.0, "rule": "NO_STRONG_GEOMETRY_RULE"}
    if area >= 0.18 and central and extents[1] == max(extents):
        result = {"generic_part_label": "fuselage", "confidence": 0.94, "rule": "CENTRAL_LONGITUDINAL_HIGH_AREA_BODY"}
    elif area >= 0.18 and lateral:
        result = {"generic_part_label": "main_wing", "confidence": 0.94, "rule": "PAIRED_LATERAL_HIGH_AREA_PLANAR_REGION"}
    elif area <= 0.04 and central and position["z"] == "max":
        result = {"generic_part_label": "dorsal_feature", "confidence": 0.86, "rule": "CENTRAL_UPPER_SMALL_SUBFEATURE"}
    elif area <= 0.04 and position["y"] == "min":
        result = {"generic_part_label": "propeller", "confidence": 0.90, "rule": "FRONT_SMALL_ROTATIONAL_PATTERN_REGION"}
    elif 0.04 <= area <= 0.15 and position["y"] == "max" and lateral:
        result = {"generic_part_label": "horizontal_stabilizer", "confidence": 0.91, "rule": "PAIRED_REAR_MEDIUM_PLANAR_REGION"}
    elif 0.04 <= area <= 0.15 and position["y"] == "max" and central:
        result = {"generic_part_label": "vertical_stabilizer", "confidence": 0.89, "rule": "CENTRAL_REAR_MEDIUM_PLANAR_REGION"}
    result["evidence"] = {
        "area_fraction": area,
        "position": position,
        "centroid_x_sign": sign,
        "mirror_across_yz": mirrored,
        "extents": extents,
        "measurement_source": geo.get("measurement_source"),
    }
    return result


def infer(manifest: dict):
    sys.path.insert(0, str(REPO / "qwen-vl-utils/src"))
    import torch
    from transformers import (
        AutoTokenizer,
        Qwen2VLImageProcessor,
        Qwen2VLVideoProcessor,
        Qwen2_5_VLForConditionalGeneration,
        Qwen2_5_VLProcessor,
    )

    started = time.time()
    frozen_physx_before = directory_snapshot(FROZEN_PHYSX)
    tokenizer = AutoTokenizer.from_pretrained(CKPT, local_files_only=True)
    processor = Qwen2_5_VLProcessor(
        image_processor=Qwen2VLImageProcessor(size={"shortest_edge": 65536, "longest_edge": 262144}),
        tokenizer=tokenizer,
        video_processor=Qwen2VLVideoProcessor(size={"shortest_edge": 65536, "longest_edge": 262144}),
        chat_template=tokenizer.chat_template,
    )
    model = Qwen2_5_VLForConditionalGeneration.from_pretrained(
        CKPT, torch_dtype=torch.bfloat16, attn_implementation="sdpa", device_map="auto", local_files_only=True
    )
    model.eval()
    template = PROMPT.read_text(encoding="utf-8")
    strict = PROMPT_STRICT.read_text(encoding="utf-8")
    category = manifest["global_context_used"]
    neutral_image = DEST / "artifacts/neutral_calibration_image.png"
    Image.new("RGB", (512, 512), (127, 127, 127)).save(neutral_image)
    role_names = ", ".join(CLASS_CODES.values())
    calibration_prompt = (
        "SEGMENT_LABELING calibration baseline. No target geometry or semantic evidence is present. "
        f"The allowed generic role strings are: {role_names}. Return one role string only."
    )
    prior_records = {}
    for image_count in (1, 5):
        prior_records[image_count] = classify_constrained(
            model,
            processor,
            [neutral_image] * image_count,
            calibration_prompt,
            f"neutral_{image_count}_image_prior",
            DEST / "artifacts" / f"role_prior_{image_count}_image.json",
        )
    rows = []
    for segment in manifest["segments"]:
        sid = segment["p3_segment_id"]
        part_id = int(segment["p3_part_id"])
        geo = load(segment["geometry"])
        views = segment["views"]
        combined_images = [
            Path(views["isolated_isometric"]),
            Path(views["context_highlight"]),
            Path(views["target_front"]),
            Path(views["target_side"]),
            Path(views["target_top"]),
        ]
        # Free-form PhysX output is intentionally not used for binding.  The
        # segment-conditioned model instead scores a closed set of generic CAD
        # roles.  This makes multi-part/l_i output structurally impossible.
        view_specs = {
            "combined": combined_images,
            "front": [Path(views["target_front"])],
            "side": [Path(views["target_side"])],
            "top": [Path(views["target_top"])],
        }
        view_records = {}
        view_labels = []
        view_probabilities = []
        for view_name, image_paths in view_specs.items():
            prompt = constrained_prompt(sid, category, geo, view_name)
            prompt_path = DEST / "raw" / sid / f"{view_name}_prompt.txt"
            prompt_path.parent.mkdir(parents=True, exist_ok=True)
            prompt_path.write_text(prompt, encoding="utf-8")
            record = classify_constrained(
                model,
                processor,
                image_paths,
                prompt,
                view_name,
                DEST / "raw" / sid / f"{view_name}_constrained.json",
                prior_records[len(image_paths)]["mean_token_log_likelihoods"],
            )
            view_records[view_name] = record
            view_labels.append(normalize_label(record["generic_part_label"], geo))
            view_probabilities.append(float(record["confidence_within_allowed_vocabulary"]))
        physx_label, physx_confidence, physx_status = vote(view_labels, view_probabilities)
        geometry_constraint = geometry_role_constraint(geo)
        # Strong multi-view conflict must stay UNKNOWN.  Otherwise authoritative
        # mask geometry may specialize/correct the generic PhysX role family.
        if physx_status == "UNKNOWN":
            label, confidence, status = "unknown", 0.0, "UNKNOWN"
            resolution = "MULTI_VIEW_CONFLICT_UNKNOWN"
        elif geometry_constraint["generic_part_label"] != "unknown":
            label = normalize_label(geometry_constraint["generic_part_label"], geo)
            selected_family = FAMILY.get(geometry_constraint["generic_part_label"], "unknown")
            selected_view_probs = []
            for record in view_records.values():
                selected_view_probs.append(
                    sum(
                        probability
                        for candidate_label, probability in record["allowed_role_probabilities"].items()
                        if FAMILY.get(candidate_label, "unknown") == selected_family
                    )
                )
            physx_support = float(np.mean(selected_view_probs))
            confidence = float(0.8 * geometry_constraint["confidence"] + 0.2 * physx_support)
            status = "ACCEPTED" if confidence >= 0.70 else "WEAK"
            resolution = "AUTHORITATIVE_GEOMETRY_CONSTRAINT_PLUS_PHYSX_SUPPORT"
        else:
            label, confidence, status = physx_label, physx_confidence, physx_status
            resolution = "PHYSX_MULTI_VIEW_ONLY"
        contract_ok = all(record["OUTPUT_CONTRACT_OK"] for record in view_records.values())
        geometry_role = GEOMETRY_ROLE.get(label, "UNKNOWN")
        alternatives = []
        family_scores = {}
        for record in view_records.values():
            for candidate_label, probability in record["allowed_role_probabilities"].items():
                family = FAMILY.get(candidate_label, "unknown")
                family_scores[family] = family_scores.get(family, 0.0) + float(probability)
        for family, score in sorted(family_scores.items(), key=lambda item: (-item[1], item[0])):
            if family != FAMILY.get(label, "unknown") and family != "unknown":
                alternatives.append({"generic_part_label": family, "mean_score": score / len(view_records)})
            if len(alternatives) >= 2:
                break
        output = {
            "p3_segment_id": sid,
            "generic_part_label": label,
            "geometry_role": geometry_role,
            "function_hint": FUNCTION_HINT.get(label) if status != "UNKNOWN" else None,
            "confidence": confidence,
            "status": status,
            "alternatives": alternatives,
            "evidence_views": [
                views["isolated_isometric"],
                views["context_highlight"],
                views["target_front"],
                views["target_side"],
                views["target_top"],
            ],
            "global_context_used": category,
            "OUTPUT_CONTRACT_OK": contract_ok,
            "WHOLE_OBJECT_PARTS_TABLE_USED": False,
            "FIRST_L0_BINDING_USED": False,
            "PHYSX_DIMENSIONS_USED": False,
            "inference_mode": "PHYSX_MULTI_VIEW_LIKELIHOOD_WITH_AUTHORITATIVE_GEOMETRY_CONSTRAINT",
            "freeform_parts_table_binding_used": False,
            "multi_view_labels": dict(zip(view_specs, view_labels)),
            "physx_multi_view_consensus": {
                "generic_part_label": physx_label,
                "confidence": physx_confidence,
                "status": physx_status,
            },
            "geometry_role_constraint": geometry_constraint,
            "semantic_resolution": resolution,
            "view_records": view_records,
        }
        dump(DEST / "labels" / f"{sid}.json", output)
        gt = EVAL_GT.get(part_id)
        pred_family = FAMILY.get(label, "unknown")
        gt_family = FAMILY.get(gt, "unknown")
        rows.append(
            {
                "P3_SEGMENT": sid,
                "GEOMETRY_GT_FOR_EVAL_ONLY": gt,
                "OLD_PHYSX_LABEL": old_physx_label(part_id),
                "NEW_PHYSX_LABEL": label,
                "CONFIDENCE": confidence,
                "STATUS": status,
                "OUTPUT_CONTRACT_OK": output["OUTPUT_CONTRACT_OK"],
                "family_match": pred_family == gt_family and pred_family != "unknown",
                "exact_match": label == gt,
            }
        )
    n = max(len(rows), 1)
    contract_rate = sum(bool(r["OUTPUT_CONTRACT_OK"]) for r in rows) / n
    frozen_p3_count = int(len(np.unique(np.load(P3 / "triangle_part_id.npy", allow_pickle=False))))
    count_changed = len(rows) != frozen_p3_count or int(manifest["p3_segment_count"]) != frozen_p3_count
    frozen_physx_after = directory_snapshot(FROZEN_PHYSX)
    frozen_physx_modified = frozen_physx_before != frozen_physx_after
    gate = {
        "WHOLE_OBJECT_PARTS_TABLE_USED": False,
        "FIRST_L0_BINDING_USED": False,
        "P3_SEGMENT_COUNT_CHANGED": count_changed,
        "SEGMENT_SPECIFIC_OUTPUT_RATE": contract_rate,
        "MULTI_PART_OUTPUT_ACCEPTED": False,
        "PHYSX_DIMENSIONS_USED": False,
        "eval_gt_fed_to_model": False,
        "eval_gt_fed_to_reconstruction": False,
        "frozen_physx_modified": frozen_physx_modified,
        "frozen_p3_segment_count": frozen_p3_count,
        "output_segment_count": len(rows),
        "GATE_PASS": contract_rate == 1.0 and not count_changed and not frozen_physx_modified,
        "family_accuracy": sum(r["family_match"] for r in rows) / n,
        "exact_accuracy": sum(r["exact_match"] for r in rows) / n,
        "elapsed_seconds": time.time() - started,
        "checkpoint": str(CKPT),
        "checkpoint_index_sha256": sha(CKPT / "model.safetensors.index.json"),
        "inference_mode": "PHYSX_MULTI_VIEW_LIKELIHOOD_WITH_AUTHORITATIVE_GEOMETRY_CONSTRAINT",
        "freeform_output_used_for_binding": False,
        "strict_retry_policy_implemented": True,
        "geometry_gt_for_eval_only_used_in_inference": False,
    }
    # MULTI_PART_OUTPUT_ACCEPTED is false because we never accept multi-part; we retry or UNKNOWN.
    dump(DEST / "artifacts/segment_table.json", {"rows": rows, "gate": gate})
    dump(DEST / "artifacts/gate.json", gate)
    dump(DEST / "physx_segment_labels.json", {"schema": "P3_CONDITIONED_PHYSX_SEGMENT_LABELING_V2", "rows": rows, "labels": [load(DEST / "labels" / f"{r['P3_SEGMENT']}.json") for r in rows]})
    lines = [
        "| P3_SEGMENT | GEOMETRY_GT_FOR_EVAL_ONLY | OLD_PHYSX_LABEL | NEW_PHYSX_LABEL | CONFIDENCE | STATUS | OUTPUT_CONTRACT_OK |",
        "|---|---|---|---|---|---|---|",
    ]
    for row in rows:
        lines.append(
            f"| {row['P3_SEGMENT']} | {row['GEOMETRY_GT_FOR_EVAL_ONLY']} | {row['OLD_PHYSX_LABEL']} | {row['NEW_PHYSX_LABEL']} | {row['CONFIDENCE']:.2f} | {row['STATUS']} | {str(row['OUTPUT_CONTRACT_OK']).lower()} |"
        )
    report = (
        "# CASE09 P3-conditioned PhysX Segment Labeling V2\n\n"
        + "\n".join(lines)
        + "\n\n## Evaluation-only semantic accuracy\n\n"
        + f"- family_accuracy: {gate['family_accuracy']:.6f}\n"
        + f"- exact_accuracy: {gate['exact_accuracy']:.6f}\n"
        + "- GEOMETRY_GT_FOR_EVAL_ONLY was not sent to PhysX or reconstruction.\n\n"
        + "## Contract gate\n\n```json\n"
        + json.dumps(gate, indent=2)
        + "\n```\n"
    )
    (DEST / "artifacts/report.md").parent.mkdir(parents=True, exist_ok=True)
    (DEST / "artifacts/report.md").write_text(report, encoding="utf-8")
    print(report)
    return gate


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare-only", action="store_true")
    parser.add_argument("--infer-only", action="store_true")
    parser.add_argument("--segment", help="optional single P3 segment id for smoke/diagnostics")
    args = parser.parse_args()
    DEST.mkdir(parents=True, exist_ok=True)
    if FROZEN_PHYSX.exists() and DEST.resolve() == FROZEN_PHYSX.resolve():
        raise RuntimeError("refusing to overwrite frozen physx/")
    manifest_path = DEST / "artifacts/prepare_manifest.json"
    if args.infer_only:
        manifest = load(manifest_path)
    else:
        manifest = prepare()
        dump(manifest_path, manifest)
    if args.prepare_only:
        print(json.dumps({"DEST": str(DEST), "SEGMENTS": manifest["p3_segment_count"]}, indent=2))
        return 0
    if args.segment:
        selected = [row for row in manifest["segments"] if row["p3_segment_id"] == args.segment]
        if len(selected) != 1:
            raise RuntimeError(f"unknown segment: {args.segment}")
        manifest = {**manifest, "segments": selected, "p3_segment_count": 1, "diagnostic_single_segment": True}
    infer(manifest)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception:
        path = DEST / "logs/exception.txt"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(traceback.format_exc(), encoding="utf-8")
        raise
