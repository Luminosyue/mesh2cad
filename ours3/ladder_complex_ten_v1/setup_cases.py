#!/usr/bin/env python3
"""Scaffold 10 unused complex tank-protocol cases."""
from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
SRC_SCRIPTS = ROOT / "ours3/cube_p3_xpart_cadfit_routea_v1/scripts"
SHARP = ROOT / "ours3/dora_ses_xpart45_v1/vendor/sharp_sample.py"
ASM_TMPL = ROOT / "ours3/ladder_more_v2/templates/build_assembly.py"
LADDER = ROOT / "ours3/ladder_complex_ten_v1"
MESHES = ROOT / "ours3/meshes"

CASES = [
    {
        "slug": "school_bus_p3_xpart_cadfit_routea_v1",
        "label": "school_bus",
        "tier": "complex_vehicle",
        "mesh": "Sonny_School_Bus.obj",
        "faces": 709952,
        "xpart_batch_size": 1,
        "why": "School bus: body+wheels+windows, tank/fire-truck class.",
    },
    {
        "slug": "cabinet_drawer_p3_xpart_cadfit_routea_v1",
        "label": "cabinet_drawer",
        "tier": "complex_furniture",
        "mesh": "meta_ADT_1_0_Apartment_CabinetDrawerC_3d.obj",
        "faces": 878612,
        "xpart_batch_size": 1,
        "why": "Cabinet with drawers; furniture assembly, not WhiteCabinet clone.",
    },
    {
        "slug": "speaker_big_p3_xpart_cadfit_routea_v1",
        "label": "speaker_big",
        "tier": "complex_appliance",
        "mesh": "meta_ADT_1_0_SpeakerBig_1_3d.obj",
        "faces": 667880,
        "xpart_batch_size": 1,
        "why": "Large speaker enclosure+grille; bigger than speaker_small.",
    },
    {
        "slug": "display_shelves_p3_xpart_cadfit_routea_v1",
        "label": "display_shelves",
        "tier": "complex_furniture",
        "mesh": "meta_ADT_1_0_DisplayShelves_1_3d.obj",
        "faces": 655370,
        "xpart_batch_size": 1,
        "why": "Multi-shelf furniture assembly.",
    },
    {
        "slug": "pound_and_roll_p3_xpart_cadfit_routea_v1",
        "label": "pound_and_roll",
        "tier": "complex_toy_mechanical",
        "mesh": "Melissa_Doug_Pound_and_Roll.obj",
        "faces": 601900,
        "xpart_batch_size": 1,
        "why": "Pound-and-roll toy: base, pegs, rolling balls.",
    },
    {
        "slug": "pressure_cooker_p3_xpart_cadfit_routea_v1",
        "label": "pressure_cooker",
        "tier": "complex_appliance",
        "mesh": "TriStar_Products_PPC_Power_Pressure_Cooker_XL_in_Black.obj",
        "faces": 563464,
        "xpart_batch_size": 1,
        "why": "Pressure cooker: pot, lid, handles.",
    },
    {
        "slug": "bunny_racer_p3_xpart_cadfit_routea_v1",
        "label": "bunny_racer",
        "tier": "complex_vehicle",
        "mesh": "BUNNY_RACER.obj",
        "faces": 466168,
        "xpart_batch_size": 1,
        "why": "Toy racer sibling of chicken_racer; wheels/chassis.",
    },
    {
        "slug": "lego_dino_hq_p3_xpart_cadfit_routea_v1",
        "label": "lego_dino_hq",
        "tier": "complex_toy_mechanical",
        "mesh": "LEGO_5887_Dino_Defense_HQ.obj",
        "faces": 418720,
        "xpart_batch_size": 1,
        "why": "LEGO Dino Defense HQ; many bricks expected.",
    },
    {
        "slug": "sorting_bus_p3_xpart_cadfit_routea_v1",
        "label": "sorting_bus",
        "tier": "complex_vehicle",
        "mesh": "SORTING_BUS.obj",
        "faces": 363408,
        "xpart_batch_size": 1,
        "why": "Sorting bus near tank face count (~367k).",
    },
    {
        "slug": "mini_excavator_p3_xpart_cadfit_routea_v1",
        "label": "mini_excavator",
        "tier": "complex_vehicle",
        "mesh": "MINI_EXCAVATOR.obj",
        "faces": 322620,
        "xpart_batch_size": 1,
        "why": "Mini excavator: tracks, boom, bucket; closest to tank structure.",
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
    if SHARP.is_file():
        shutil.copy2(SHARP, case_root / "dora_ses/vendor/sharp_sample.py")

    src = MESHES / spec["mesh"]
    dst = case_root / "source" / spec["mesh"]
    if not dst.is_file():
        shutil.copy2(src, dst)

    spec = dict(spec)
    spec["case_root"] = str(case_root)
    spec["source_copied"] = str(dst)
    spec["source_bytes"] = dst.stat().st_size
    return spec


def main() -> None:
    LADDER.mkdir(parents=True, exist_ok=True)
    (LADDER / "logs").mkdir(exist_ok=True)
    created = [setup_case(spec) for spec in CASES]
    payload = {
        "name": "ladder_complex_ten_v1",
        "protocol": "tank_p3_xpart_dora_wait_cadfit_routea_assembly",
        "P3_RECIPE": {"prompt_num": 4000, "prompt_bs": 4, "point_num": "min(n_faces, 400000)"},
        "XPART": {"octree": 512, "batch_size": 1, "empty_scene_export": "skip", "octree256_retry": True},
        "CADFIT": {"max_iterations": 1, "fillet": "OFF", "jobs": 1, "inner_workers": 4, "dora_edge_priors": True, "dora_threshold": 25},
        "assembly": "uniform_scale_max_extent + centroid_translation (tank Route A)",
        "cases": created,
    }
    (LADDER / "cases.json").write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"created": [{k: c[k] for k in ("label", "slug", "faces", "xpart_batch_size")} for c in created]}, indent=2))


if __name__ == "__main__":
    main()
