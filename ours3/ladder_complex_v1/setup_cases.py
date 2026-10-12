#!/usr/bin/env python3
"""Create/patch complex tank-protocol cases: P3 -> X-Part -> CADFit Route A -> STEP -> assembly."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SRC_SCRIPTS = ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1/scripts"
SHARP = ROOT / "ours3/dora_ses_xpart45_v1/vendor/sharp_sample.py"
ASM_TMPL = ROOT / "ours3/ladder_more_v2/templates/build_assembly.py"
LADDER = ROOT / "ours3/ladder_complex_v1"
MESHES = ROOT / "ours3/meshes"

CASES = [
    {
        "slug": "recordplayer_p3_xpart_cadfit_routea_v1",
        "label": "recordplayer",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_RecordPlayer_1_3d.obj",
        "faces": 1026406,
        "xpart_batch_size": 4,
        "resume_p3": True,
        "why": "Platter + tonearm + enclosure. P3 already frozen at 16 parts.",
    },
    {
        "slug": "winerack_p3_xpart_cadfit_routea_v1",
        "label": "winerack",
        "tier": "complex_lattice",
        "mesh": "meta_ADT_1_0_WoodenWineRack_3d.obj",
        "faces": 900624,
        "xpart_batch_size": 1,
        "resume_p3": True,
        "why": "Repeated lattice / slots. P3 already frozen at 34 parts (toaster-scale).",
    },
    {
        "slug": "paintmaker_p3_xpart_cadfit_routea_v1",
        "label": "paintmaker",
        "tier": "complex_toy_mechanical",
        "mesh": "Paint_Maker.obj",
        "faces": 1013436,
        "xpart_batch_size": 4,
        "resume_p3": False,
        "why": "Toy machine with many mechanical parts. Structurally closer to robot/tank than a box.",
    },
    {
        "slug": "birdhouse_p3_xpart_cadfit_routea_v1",
        "label": "birdhouse",
        "tier": "complex_architectural",
        "mesh": "meta_DTC_1_0_BirdHouse_B08DK32YVT_WhitePorchWhiteWalls_3d.obj",
        "faces": 1269372,
        "xpart_batch_size": 4,
        "resume_p3": False,
        "why": "Porch + walls + roof assembly. Architectural multi-body, high-poly scan.",
    },
]


def write_paths(case_root: Path, mesh_name: str) -> None:
    text = textwrap.dedent(
        f"""\
        #!/usr/bin/env python3
        \"\"\"Route A case paths. Independent of tank/airplane/robot scripts.\"\"\"

        from pathlib import Path

        ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
        CASE = ROOT / "ours3/{case_root.name}"
        SOURCE = CASE / "source/{mesh_name}"
        SOURCE_ORIG = ROOT / "ours3/meshes/{mesh_name}"
        P3_DIR = CASE / "p3"
        XPART_DIR = CASE / "xpart"
        DORA_DIR = CASE / "dora_ses"
        CADFIT_DIR = CASE / "cadfit_routea"
        STL_DIR = CADFIT_DIR / "input_stl"
        CADFIT_RAW = CADFIT_DIR / "cadfit_raw"
        STEP_DIR = CADFIT_DIR / "step"
        LOGS = CASE / "logs"

        HUNYUAN_PY = Path("/data/miniconda3/envs/hunyuan/bin/python")
        HY3D_PY = Path("/data/miniconda3/envs/hy3d/bin/python")
        CADFIT_PY = Path("/data/miniconda3/envs/cadfit-env/bin/python")
        BLENDER_PY = Path("/data/home/hhfzhang/.conda/envs/blender/bin/python")
        CADFIT_REPO = ROOT / "CADFit"
        XPART_ROOT = ROOT / "Hunyuan3D-Part/XPart"
        P3_ROOT = ROOT / "Hunyuan3D-Part/P3-SAM"
        HY3DGEN_MODELS = ROOT / "ours3/.cache/xpart"
        """
    )
    (case_root / "scripts/paths.py").write_text(text, encoding="utf-8")


def setup_case(spec: dict) -> dict:
    case_root = ROOT / "ours3" / spec["slug"]
    scripts = case_root / "scripts"
    scripts.mkdir(parents=True, exist_ok=True)
    (case_root / "source").mkdir(exist_ok=True)
    (case_root / "logs").mkdir(exist_ok=True)
    (case_root / "dora_ses/vendor").mkdir(parents=True, exist_ok=True)
    (case_root / "artifacts").mkdir(exist_ok=True)
    (case_root / "cadfit_routea/input_stl").mkdir(parents=True, exist_ok=True)
    (case_root / "cadfit_routea/cadfit_raw").mkdir(parents=True, exist_ok=True)
    (case_root / "cadfit_routea/step").mkdir(parents=True, exist_ok=True)

    for py in SRC_SCRIPTS.glob("*.py"):
        if py.name == "paths.py":
            continue
        shutil.copy2(py, scripts / py.name)
    shutil.copy2(ASM_TMPL, scripts / "build_assembly.py")
    write_paths(case_root, spec["mesh"])
    shutil.copy2(SHARP, case_root / "dora_ses/vendor/sharp_sample.py")

    src = MESHES / spec["mesh"]
    dst = case_root / "source" / spec["mesh"]
    if not dst.is_file():
        shutil.copy2(src, dst)

    p3_meta = case_root / "p3/part_metadata.json"
    p3_parts = None
    if p3_meta.is_file():
        p3_parts = json.loads(p3_meta.read_text()).get("num_parts")

    spec = dict(spec)
    spec["case_root"] = str(case_root)
    spec["source_copied"] = str(dst)
    spec["source_bytes"] = dst.stat().st_size
    spec["p3_parts_existing"] = p3_parts
    return spec


def main() -> None:
    LADDER.mkdir(parents=True, exist_ok=True)
    (LADDER / "logs").mkdir(exist_ok=True)
    created = [setup_case(spec) for spec in CASES]
    payload = {
        "name": "ladder_complex_v1",
        "protocol": "tank_p3_xpart_dora_fork_cadfit_routea_assembly",
        "P3_RECIPE": {"prompt_num": 4000, "prompt_bs": 4, "point_num": "min(n_faces, 400000)"},
        "XPART": {"octree": 512, "empty_scene_export": "skip"},
        "CADFIT": {"max_iterations": 1, "fillet": "OFF", "jobs": 3, "inner_workers": 8},
        "assembly": "uniform_scale_max_extent + centroid_translation (tank Route A)",
        "cases": created,
    }
    (LADDER / "cases.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"created": [{k: c[k] for k in ("label", "slug", "p3_parts_existing", "xpart_batch_size")} for c in created]}, indent=2))


if __name__ == "__main__":
    main()
