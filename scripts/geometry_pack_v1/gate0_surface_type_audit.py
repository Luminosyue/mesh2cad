#!/usr/bin/env python3
"""Gate 0: classify B-Rep face surface types for geometry_pack_v1 (no training).

Traverses TopoDS_Face of each sample's STEP via OCC BRepAdaptor_Surface.
Paper buckets:
  Analytic  = Plane / Cylinder / Cone / Sphere / Torus
  Extrusion / Revolution kept separate
  Freeform  = Bezier / BSpline only
  Other     = Offset / OtherSurface / unknown
"""

from __future__ import annotations

import argparse
import json
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PACK = ROOT / "cad_spatial_dataset/DeepCAD/geometry_pack_v1"

# Canonical display names (paper table order)
TYPE_ORDER = [
    "Plane",
    "Cylinder",
    "Cone",
    "Sphere",
    "Torus",
    "Extrusion",
    "Revolution",
    "BSpline",
    "Bezier",
    "Offset",
    "Other",
]

OCC_TO_NAME = {
    "GeomAbs_Plane": "Plane",
    "GeomAbs_Cylinder": "Cylinder",
    "GeomAbs_Cone": "Cone",
    "GeomAbs_Sphere": "Sphere",
    "GeomAbs_Torus": "Torus",
    "GeomAbs_SurfaceOfExtrusion": "Extrusion",
    "GeomAbs_SurfaceOfRevolution": "Revolution",
    "GeomAbs_BSplineSurface": "BSpline",
    "GeomAbs_BezierSurface": "Bezier",
    "GeomAbs_OffsetSurface": "Offset",
    "GeomAbs_OtherSurface": "Other",
}

ANALYTIC = {"Plane", "Cylinder", "Cone", "Sphere", "Torus"}
FREEFORM = {"Bezier", "BSpline"}


def resolve_step(sample_dir: Path) -> Path:
    meta = sample_dir / "metadata.json"
    if meta.is_file():
        data = json.loads(meta.read_text(encoding="utf-8"))
        step = Path(data.get("cad_target", {}).get("model_step", ""))
        if step.is_file():
            return step
    # fallbacks
    for cand in (
        sample_dir / "model.step",
        ROOT / "cad_spatial_dataset/DeepCAD/train" / sample_dir.name / "model.step",
    ):
        if cand.is_file():
            return cand
    raise FileNotFoundError(f"{sample_dir.name}: no STEP")


def classify_step_faces(step_path: Path) -> dict[str, int]:
    from OCP.BRepAdaptor import BRepAdaptor_Surface
    from OCP.IFSelect import IFSelect_RetDone
    from OCP.STEPControl import STEPControl_Reader
    from OCP.TopAbs import TopAbs_FACE
    from OCP.TopExp import TopExp_Explorer
    from OCP.TopoDS import TopoDS

    reader = STEPControl_Reader()
    if reader.ReadFile(str(step_path)) != IFSelect_RetDone:
        raise RuntimeError(f"STEP read failed: {step_path}")
    if not reader.TransferRoots():
        raise RuntimeError(f"STEP transfer failed: {step_path}")
    shape = reader.OneShape()
    if shape.IsNull():
        raise RuntimeError(f"empty STEP: {step_path}")

    counts: Counter[str] = Counter()
    exp = TopExp_Explorer(shape, TopAbs_FACE)
    while exp.More():
        face = TopoDS.Face_s(exp.Current())
        surf = BRepAdaptor_Surface(face)
        key = str(surf.GetType())
        # OCP may return enum name or "GeomAbs_SurfaceType.GeomAbs_Plane"
        if "." in key:
            key = key.split(".")[-1]
        name = OCC_TO_NAME.get(key, "Other")
        counts[name] += 1
        exp.Next()
    return dict(counts)


def list_sample_dirs(root: Path, *, require_metadata: bool) -> list[Path]:
    dirs = sorted(p for p in root.iterdir() if p.is_dir())
    if require_metadata:
        return [p for p in dirs if (p / "metadata.json").is_file()]
    return [p for p in dirs if (p / "model.step").is_file()]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument(
        "--pack-dir",
        type=Path,
        default=None,
        help="geometry_pack_v1-style dir (uses metadata.json -> model.step)",
    )
    ap.add_argument(
        "--train-dir",
        type=Path,
        default=None,
        help="train pool dir; each sample must contain model.step",
    )
    ap.add_argument("--name", type=str, default=None, help="dataset label for reports")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--out-json", type=Path, default=None)
    ap.add_argument("--out-md", type=Path, default=None)
    args = ap.parse_args()

    if args.pack_dir is None and args.train_dir is None:
        args.pack_dir = DEFAULT_PACK

    if args.pack_dir is not None:
        sample_root = args.pack_dir
        sample_dirs = list_sample_dirs(sample_root, require_metadata=True)
        resolve = resolve_step
        label = args.name or sample_root.name
    else:
        sample_root = args.train_dir
        sample_dirs = list_sample_dirs(sample_root, require_metadata=False)
        resolve = lambda d: d / "model.step"
        label = args.name or sample_root.parent.name

    if args.limit is not None:
        sample_dirs = sample_dirs[: args.limit]

    out_json = args.out_json or (sample_root / "gate0_surface_type_audit.json")
    out_md = args.out_md or (sample_root / "gate0_surface_type_audit.md")

    face_totals: Counter[str] = Counter()
    parts_with: dict[str, set[str]] = defaultdict(set)
    per_sample: list[dict] = []
    failed: list[dict] = []

    for i, d in enumerate(sample_dirs):
        sid = d.name
        try:
            step = resolve(d)
            counts = classify_step_faces(step)
            n_faces = int(sum(counts.values()))
            freeform_faces = int(sum(counts.get(t, 0) for t in FREEFORM))
            analytic_faces = int(sum(counts.get(t, 0) for t in ANALYTIC))
            for t, n in counts.items():
                face_totals[t] += n
                if n > 0:
                    parts_with[t].add(sid)
            per_sample.append(
                {
                    "sample_id": sid,
                    "step": str(step),
                    "n_faces": n_faces,
                    "counts": counts,
                    "freeform_faces": freeform_faces,
                    "analytic_faces": analytic_faces,
                    "has_freeform": freeform_faces > 0,
                }
            )
            if (i + 1) % 50 == 0 or i == 0 or i + 1 == len(sample_dirs):
                print(
                    f"[{i + 1}/{len(sample_dirs)}] {sid} faces={n_faces} "
                    f"freeform={freeform_faces} types={counts}",
                    flush=True,
                )
        except Exception as exc:  # noqa: BLE001
            failed.append({"sample_id": sid, "error": f"{type(exc).__name__}: {exc}"})
            print(f"[{i + 1}/{len(sample_dirs)}] FAIL {sid}: {exc}", flush=True)

    total_parts = len(per_sample)
    total_faces = int(sum(face_totals.values()))
    freeform_faces = int(sum(face_totals.get(t, 0) for t in FREEFORM))
    parts_with_freeform = len(parts_with["Bezier"] | parts_with["BSpline"])
    freeform_face_ratio = (freeform_faces / total_faces) if total_faces else 0.0
    analytic_faces = int(sum(face_totals.get(t, 0) for t in ANALYTIC))

    table_rows = []
    for t in TYPE_ORDER:
        faces = int(face_totals.get(t, 0))
        parts = len(parts_with.get(t, set()))
        table_rows.append(
            {
                "surface_type": t,
                "faces": faces,
                "parts_containing_type": parts,
                "bucket": (
                    "Analytic"
                    if t in ANALYTIC
                    else "Freeform"
                    if t in FREEFORM
                    else "Extrusion"
                    if t == "Extrusion"
                    else "Revolution"
                    if t == "Revolution"
                    else "Other"
                ),
            }
        )

    freeform_ids = sorted(parts_with["Bezier"] | parts_with["BSpline"])
    summary = {
        "gate": "Gate0_surface_type_audit",
        "dataset": label,
        "sample_root": str(sample_root),
        "TOTAL_PARTS": total_parts,
        "TOTAL_FACES": total_faces,
        "ANALYTIC_FACES": analytic_faces,
        "FREEFORM_FACES": freeform_faces,
        "PARTS_WITH_FREEFORM": parts_with_freeform,
        "FREEFORM_FACE_RATIO": freeform_face_ratio,
        "PARTS_WITH_EXTRUSION": len(parts_with.get("Extrusion", set())),
        "PARTS_WITH_REVOLUTION": len(parts_with.get("Revolution", set())),
        "table": table_rows,
        "freeform_sample_ids_head": freeform_ids[:50],
        "failed": failed[:50],
        "n_failed": len(failed),
        "samples": per_sample,
    }

    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_json.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    lines = [
        f"# Gate 0 — B-Rep face surface types (`{label}`)",
        "",
        f"- TOTAL_PARTS = **{total_parts}**",
        f"- TOTAL_FACES = **{total_faces}**",
        f"- ANALYTIC_FACES (Plane/Cylinder/Cone/Sphere/Torus) = **{analytic_faces}**",
        f"- FREEFORM_FACES (Bezier+BSpline only) = **{freeform_faces}**",
        f"- PARTS_WITH_FREEFORM = **{parts_with_freeform}**",
        f"- FREEFORM_FACE_RATIO = **{freeform_face_ratio:.6f}**",
        f"- PARTS_WITH_EXTRUSION = **{len(parts_with.get('Extrusion', set()))}**",
        f"- PARTS_WITH_REVOLUTION = **{len(parts_with.get('Revolution', set()))}**",
        f"- n_failed = **{len(failed)}**",
        "",
        "| Surface type | Faces | Parts containing type | Bucket |",
        "|---|---:|---:|---|",
    ]
    for row in table_rows:
        lines.append(
            f"| {row['surface_type']} | {row['faces']} | "
            f"{row['parts_containing_type']} | {row['bucket']} |"
        )
    if freeform_ids:
        lines += ["", "## Parts with Freeform (Bezier/BSpline)", ""]
        for sid in freeform_ids[:100]:
            lines.append(f"- `{sid}`")
        if len(freeform_ids) > 100:
            lines.append(f"- ... (+{len(freeform_ids) - 100} more)")
    if failed:
        lines += ["", "## Failures (head)", ""]
        for f in failed[:30]:
            lines.append(f"- `{f['sample_id']}`: {f['error']}")
    lines.append("")
    out_md.write_text("\n".join(lines), encoding="utf-8")

    slim = {k: summary[k] for k in summary if k != "samples"}
    print(json.dumps(slim, indent=2))
    print(f"wrote {out_md}")
    print(f"wrote {out_json}")
    return 0 if not failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
