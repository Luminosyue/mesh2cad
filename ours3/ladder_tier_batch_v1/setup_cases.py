#!/usr/bin/env python3
"""Create tier A–D batch cases: P3 -> X-Part -> CADFit Route A -> STEP -> assembly."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SRC_SCRIPTS = ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1/scripts"
SHARP = ROOT / "ours3/dora_ses_xpart45_v1/vendor/sharp_sample.py"
ASM_TMPL = ROOT / "ours3/ladder_more_v2/templates/build_assembly.py"
LADDER = ROOT / "ours3/ladder_tier_batch_v1"
MESHES = ROOT / "ours3/meshes"

CASES = [
    {
        "slug": "speaker_small_p3_xpart_cadfit_routea_v1",
        "label": "speaker_small",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_SpeakerSmall_1_3d.obj",
        "faces": 1176826,
        "xpart_batch_size": 4,
        "why": "Grille + enclosure; recordplayer/toaster tier.",
    },
    {
        "slug": "food_processor_p3_xpart_cadfit_routea_v1",
        "label": "food_processor",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_FoodProcessor_1_3d.obj",
        "faces": 701994,
        "xpart_batch_size": 4,
        "why": "Blade bowl + lid multi-component kitchen appliance.",
    },
    {
        "slug": "dvd_player_p3_xpart_cadfit_routea_v1",
        "label": "dvd_player",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_DvdPlayer_1_3d.obj",
        "faces": 679300,
        "xpart_batch_size": 4,
        "why": "Tray + chassis assembly.",
    },
    {
        "slug": "humidifier_p3_xpart_cadfit_routea_v1",
        "label": "humidifier",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_Humidifier_1_3d.obj",
        "faces": 638626,
        "xpart_batch_size": 4,
        "why": "Tank + shell; rotational + assembly mix.",
    },
    {
        "slug": "construction_30_p3_xpart_cadfit_routea_v1",
        "label": "construction_30",
        "tier": "complex_toy_mechanical",
        "mesh": "30_CONSTRUCTION_SET.obj",
        "faces": 385828,
        "xpart_batch_size": 4,
        "why": "Multi-block toy assembly; robot/car tier.",
    },
    {
        "slug": "construction_60_p3_xpart_cadfit_routea_v1",
        "label": "construction_60",
        "tier": "complex_toy_mechanical",
        "mesh": "60_CONSTRUCTION_SET.obj",
        "faces": 304942,
        "xpart_batch_size": 4,
        "why": "Larger construction set; many parts expected.",
    },
    {
        "slug": "fire_truck_p3_xpart_cadfit_routea_v1",
        "label": "fire_truck",
        "tier": "complex_vehicle",
        "mesh": "FIRE_TRUCK.obj",
        "faces": 465260,
        "xpart_batch_size": 4,
        "why": "Low-poly vehicle like car.",
    },
    {
        "slug": "coast_guard_boat_p3_xpart_cadfit_routea_v1",
        "label": "coast_guard_boat",
        "tier": "complex_vehicle",
        "mesh": "COAST_GUARD_BOAT.obj",
        "faces": 332256,
        "xpart_batch_size": 4,
        "why": "Hull + superstructure; complements airplane.",
    },
    {
        "slug": "fairy_tale_blocks_p3_xpart_cadfit_routea_v1",
        "label": "fairy_tale_blocks",
        "tier": "complex_toy_mechanical",
        "mesh": "FAIRY_TALE_BLOCKS.obj",
        "faces": 556192,
        "xpart_batch_size": 4,
        "why": "Irregular block combo; harder topology than rubiks.",
    },
    {
        "slug": "kitch_island_p3_xpart_cadfit_routea_v1",
        "label": "kitch_island",
        "tier": "complex_architectural",
        "mesh": "meta_ADT_1_0_KitchIsland_3d.obj",
        "faces": 654408,
        "xpart_batch_size": 4,
        "why": "Large kitchen island furniture assembly.",
    },
    {
        "slug": "birdhouse_toy_p3_xpart_cadfit_routea_v1",
        "label": "birdhouse_toy",
        "tier": "complex_architectural",
        "mesh": "meta_ADT_1_0_BirdHouseToy_3d.obj",
        "faces": 1067392,
        "xpart_batch_size": 4,
        "why": "Birdhouse alt; porch + roof architectural.",
    },
    {
        "slug": "building_5i_p3_xpart_cadfit_routea_v1",
        "label": "building_5i",
        "tier": "complex_architectural",
        "mesh": "5iHumoHAKIPuELpWrRd3Vr3mk38.obj",
        "faces": 706310,
        "xpart_batch_size": 4,
        "why": "Building-scale cross-case generalization.",
    },
    {
        "slug": "pottery_large_p3_xpart_cadfit_routea_v1",
        "label": "pottery_large",
        "tier": "stress_rotational",
        "mesh": "meta_DTC_1_0_Pottery_B083SFB7T5_Large_3d.obj",
        "faces": 2152372,
        "xpart_batch_size": 1,
        "why": "Highest poly rotational stress test.",
    },
    {
        "slug": "white_cabinet_p3_xpart_cadfit_routea_v1",
        "label": "white_cabinet",
        "tier": "stress_furniture",
        "mesh": "meta_ADT_1_0_WhiteCabinet_1_3d.obj",
        "faces": 1612516,
        "xpart_batch_size": 1,
        "why": "Large cabinet; many parts expected.",
    },
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
    if "stage_assembly" in text and '"assembly"' in text:
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
    if 'if "assembly" in stages:' not in text:
        text = text.replace(
            '        if "step" in stages:\n            stage_step(log_path)\n            write_progress("step")\n',
            '        if "step" in stages:\n            stage_step(log_path)\n            write_progress("step")\n'
            '        if "assembly" in stages:\n            stage_assembly(log_path)\n            write_progress("assembly")\n',
        )
    if "def stage_assembly" not in text:
        text = text.replace(
            "def write_progress(stage: str, extra: dict | None = None) -> None:",
            PIPELINE_STAGE_ASSEMBLY + "def write_progress(stage: str, extra: dict | None = None) -> None:",
        )
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
    (case_root / "cadfit_routea/input_stl").mkdir(parents=True, exist_ok=True)
    (case_root / "cadfit_routea/cadfit_raw").mkdir(parents=True, exist_ok=True)
    (case_root / "cadfit_routea/step").mkdir(parents=True, exist_ok=True)
    (case_root / "assembly").mkdir(exist_ok=True)

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
    if not src.is_file():
        raise FileNotFoundError(src)
    if not dst.is_file():
        shutil.copy2(src, dst)

    spec = dict(spec)
    spec["case_root"] = str(case_root)
    spec["source_copied"] = str(dst)
    spec["source_bytes"] = dst.stat().st_size
    spec["p3_parts_existing"] = None
    p3_meta = case_root / "p3/part_metadata.json"
    if p3_meta.is_file():
        spec["p3_parts_existing"] = json.loads(p3_meta.read_text()).get("num_parts")
    return spec


def main() -> None:
    LADDER.mkdir(parents=True, exist_ok=True)
    (LADDER / "logs").mkdir(exist_ok=True)
    created = [setup_case(spec) for spec in CASES]
    payload = {
        "name": "ladder_tier_batch_v1",
        "protocol": "tank_p3_xpart_dora_fork_cadfit_routea_assembly",
        "P3_RECIPE": {"prompt_num": 4000, "prompt_bs": 4, "point_num": "min(n_faces, 400000)"},
        "XPART": {"octree": 512, "empty_scene_export": "skip"},
        "CADFIT": {"max_iterations": 1, "fillet": "OFF", "jobs": 1, "inner_workers": 4},
        "assembly": "uniform_scale_max_extent + centroid_translation (tank Route A)",
        "cases": created,
    }
    (LADDER / "cases.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"created": [c["label"] for c in created]}, indent=2))


if __name__ == "__main__":
    main()
