#!/usr/bin/env python3
"""Create more tank-protocol cases and launch P3→X-Part→CADFit→STEP→assembly."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SRC_SCRIPTS = ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1/scripts"
SHARP = ROOT / "ours3/dora_ses_xpart45_v1/vendor/sharp_sample.py"
ASM_TMPL = ROOT / "ours3/ladder_more_v2/templates/build_assembly.py"
LADDER = ROOT / "ours3/ladder_more_v2"
MESHES = ROOT / "ours3/meshes"

CASES = [
    {
        "slug": "rubiks_p3_xpart_cadfit_routea_v1",
        "label": "rubiks",
        "tier": "simple_geometric",
        "mesh": "meta_DTC_1_0_Toy_Puzzle_559F907A_RubiksCube_1_3d.obj",
        "faces": 846452,
        "why": "Regular cubelets; CAD-like primitives. Simpler topology than tank.",
    },
    {
        "slug": "vase_p3_xpart_cadfit_routea_v1",
        "label": "vase",
        "tier": "simple_rotational",
        "mesh": "meta_ADT_1_0_BlackVaseSmall_1_3d.obj",
        "faces": 979356,
        "why": "Revolved body, similar to canister. High-poly scan.",
    },
    {
        "slug": "winerack_p3_xpart_cadfit_routea_v1",
        "label": "winerack",
        "tier": "medium_lattice",
        "mesh": "meta_ADT_1_0_WoodenWineRack_3d.obj",
        "faces": 900624,
        "why": "Repeated lattice / slots. Assembly-like without tank-level complexity.",
    },
    {
        "slug": "recordplayer_p3_xpart_cadfit_routea_v1",
        "label": "recordplayer",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_RecordPlayer_1_3d.obj",
        "faces": 1026406,
        "why": "Platter + arm + enclosure. More parts than a box/vase.",
    },
]

EXISTING_TO_PATCH = [
    ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1",
    ROOT / "ours3/toaster_p3_xpart_cadfit_routea_v1",
    ROOT / "ours3/car_p3_xpart_cadfit_routea_v1",
]

PIPELINE_STAGE_ASSEMBLY = '''
def stage_assembly(log_path: Path) -> None:
    rc = run_cmd(
        [str(CADFIT_PY), "-u", str(_HERE / "build_assembly.py")],
        CASE,
        log_path,
    )
    if rc != 0:
        raise RuntimeError(f"assembly failed rc={rc}")
    log("assembly done", log_path)

'''


def patch_pipeline(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if "stage_assembly" in text:
        return
    text = text.replace(
        'choices=["all", "source", "p3", "xpart", "stl", "dora", "cadfit", "step", "frontend"],',
        'choices=["all", "source", "p3", "xpart", "stl", "dora", "cadfit", "step", "frontend", "assembly"],',
    )
    text = text.replace(
        '"all": ["source", "p3", "xpart", "stl", "dora", "cadfit", "step"],',
        '"all": ["source", "p3", "xpart", "stl", "dora", "cadfit", "step", "assembly"],',
    )
    if '"assembly": ["assembly"]' not in text:
        text = text.replace(
            '"step": ["step"],\n    }[args.stage]',
            '"step": ["step"],\n        "assembly": ["assembly"],\n    }[args.stage]',
        )
    if "if \"assembly\" in stages:" not in text:
        text = text.replace(
            '        if "step" in stages:\n            stage_step(log_path)\n            write_progress("step")\n',
            '        if "step" in stages:\n            stage_step(log_path)\n            write_progress("step")\n'
            '        if "assembly" in stages:\n            stage_assembly(log_path)\n            write_progress("assembly")\n',
        )
    if "def stage_assembly" not in text:
        text = text.replace("def write_progress(stage: str, extra: dict | None = None) -> None:", PIPELINE_STAGE_ASSEMBLY + "def write_progress(stage: str, extra: dict | None = None) -> None:")
    path.write_text(text, encoding="utf-8")


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

    for py in SRC_SCRIPTS.glob("*.py"):
        if py.name == "paths.py":
            continue
        shutil.copy2(py, scripts / py.name)
    shutil.copy2(ASM_TMPL, scripts / "build_assembly.py")
    write_paths(case_root, spec["mesh"])
    patch_pipeline(scripts / "run_pipeline.py")
    shutil.copy2(SHARP, case_root / "dora_ses/vendor/sharp_sample.py")

    src = MESHES / spec["mesh"]
    dst = case_root / "source" / spec["mesh"]
    if not dst.is_file():
        shutil.copy2(src, dst)
    spec = dict(spec)
    spec["case_root"] = str(case_root)
    spec["source_copied"] = str(dst)
    spec["source_bytes"] = dst.stat().st_size
    spec["gpu"] = 4
    return spec


def main() -> None:
    LADDER.mkdir(parents=True, exist_ok=True)
    (LADDER / "logs").mkdir(exist_ok=True)

    for case in EXISTING_TO_PATCH:
        scripts = case / "scripts"
        if not scripts.is_dir():
            continue
        shutil.copy2(ASM_TMPL, scripts / "build_assembly.py")
        patch_pipeline(scripts / "run_pipeline.py")
        print(f"patched assembly into {case.name}")

    created = [setup_case(spec) for spec in CASES]
    payload = {
        "name": "ladder_more_v2",
        "protocol": "tank_p3_xpart_dora_fork_cadfit_routea_assembly",
        "P3_RECIPE": {"prompt_num": 4000, "prompt_bs": 4, "point_num": "min(n_faces, 400000)"},
        "XPART": {"octree": 512, "batch_size": 10},
        "CADFIT": {"max_iterations": 1, "fillet": "OFF", "jobs": 2, "inner_workers": 8},
        "assembly": "uniform_scale_max_extent + centroid_translation (tank Route A)",
        "cases": created,
    }
    (LADDER / "cases.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"created": [c["label"] for c in created]}, indent=2))


if __name__ == "__main__":
    main()
