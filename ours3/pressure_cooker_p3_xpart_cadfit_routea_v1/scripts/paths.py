#!/usr/bin/env python3
"""Route A case paths. Independent of tank/airplane/robot scripts."""

from pathlib import Path

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
CASE = ROOT / "ours3/pressure_cooker_p3_xpart_cadfit_routea_v1"
SOURCE = CASE / "source/TriStar_Products_PPC_Power_Pressure_Cooker_XL_in_Black.obj"
SOURCE_ORIG = ROOT / "ours3/meshes/TriStar_Products_PPC_Power_Pressure_Cooker_XL_in_Black.obj"
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
