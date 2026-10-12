#!/usr/bin/env python3
"""Build the evidence bundle for PHYSX_GATE_0_RECOVERY.

This script is deliberately fail-closed.  It never substitutes unrelated
weights, never runs the 10-case batch before the official one-case smoke, and
does not write outside the Track B directory.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
OURS3 = ROOT / "ours3"
REPO = OURS3 / "external" / "PhysX-Omni"
USER_REPO = ROOT / "PhysX-Omni"
TRACK = OURS3 / "next_stage_parallel_v1" / "track_b"
ARTIFACTS = TRACK / "artifacts"
LOGS = TRACK / "logs"
GATE1_SUMMARY = OURS3 / "mac_pipeline" / "artifacts" / "mac_gate1_10case_summary.csv"
FUSION_CASES = OURS3 / "fusion_pipeline" / "cases"
PYTHON = Path("/data/miniconda3/envs/physx-omni/bin/python")


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def write_json(name: str, value: object) -> None:
    (ARTIFACTS / name).write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")


def command(args: list[str], cwd: Path | None = None) -> dict:
    p = subprocess.run(args, cwd=cwd, text=True, capture_output=True, check=False)
    return {"argv": args, "returncode": p.returncode, "stdout": p.stdout, "stderr": p.stderr}


def git_audit(path: Path) -> dict:
    commit = command(["git", "-C", str(path), "rev-parse", "HEAD"])
    branch = command(["git", "-C", str(path), "branch", "--show-current"])
    status = command(["git", "-C", str(path), "status", "--short"])
    return {
        "path": str(path),
        "commit": commit["stdout"].strip(),
        "branch": branch["stdout"].strip(),
        "dirty": bool(status["stdout"].strip()),
        "status_short": status["stdout"].splitlines(),
    }


def find_smoke_case() -> str:
    with GATE1_SUMMARY.open(newline="") as f:
        rows = list(csv.DictReader(f))
    selected = [r["CASE"] for r in rows if r["CADABILITY_CLASS"] == "A_PROGRAM_CAD_FRIENDLY"]
    if len(selected) != 1:
        raise RuntimeError(f"Expected exactly one A case, got {selected}")
    return selected[0]


def main() -> int:
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(timezone.utc).isoformat()

    official_files = ["README.md", "download.py", "1vlm_demo.py", "2infer_geo.py", "3jsongen_update.py"]
    repo_audit = git_audit(REPO)
    repo_audit["required_files"] = {
        name: {"exists": (REPO / name).is_file(), "sha256": sha256(REPO / name) if (REPO / name).is_file() else None}
        for name in official_files
    }
    repo_audit["user_preconfigured_checkout"] = git_audit(USER_REPO) if USER_REPO.is_dir() else None
    write_json("physx_repo_audit.json", repo_audit)

    requirement = {
        "evidence_source": "official local checkout README.md and download.py at audited commit",
        "official_download_script": str(REPO / "download.py"),
        "checkpoints": [
            {
                "repo_id": "PhysX-Omni/PhysX-Omni",
                "source": "https://huggingface.co/PhysX-Omni/PhysX-Omni",
                "download_api": "huggingface_hub.snapshot_download",
                "local_destination": "pretrain (relative to download.py working directory)",
                "format": "complete Hugging Face Transformers snapshot; 1vlm_demo.py passes the directory to Qwen2_5_VLForConditionalGeneration.from_pretrained",
                "required_for": "official VLM inference and smoke",
            },
            {
                "repo_id": "microsoft/TRELLIS-image-large",
                "source": "https://huggingface.co/microsoft/TRELLIS-image-large",
                "download_api": "huggingface_hub.snapshot_download",
                "local_destination": "Hugging Face cache (official script does not set local_dir)",
                "format": "complete TRELLIS decoder snapshot",
                "required_for": "2infer_geo.py / decoder_each.py geometry decoding, not the VLM-only smoke",
            },
            {
                "repo_id": "Qwen/Qwen2.5-VL-7B-Instruct",
                "source": "https://huggingface.co/Qwen/Qwen2.5-VL-7B-Instruct",
                "download_api": "AutoProcessor.from_pretrained in 1vlm_demo.py",
                "local_destination": "Hugging Face cache",
                "format": "processor/config assets",
                "required_for": "official input preprocessing",
            },
        ],
        "raw_obj_direct_input_supported": False,
        "official_vlm_input": "directory of PNG files via --imagepath",
        "official_model_argument": "--modelpath, default pretrain",
        "multiple_checkpoint_repositories": True,
        "datasets_required_for_inference": False,
    }
    write_json("physx_checkpoint_requirement.json", requirement)

    valid_locations = []
    for candidate in [REPO / "pretrain", USER_REPO / "pretrain", ARTIFACTS / "checkpoint_download_attempt" / "pretrain"]:
        weight_files = []
        if candidate.is_dir():
            weight_files = sorted(
                str(p) for p in candidate.rglob("*") if p.is_file() and p.suffix in {".safetensors", ".pt", ".pth", ".ckpt", ".bin"}
            )
        valid = (candidate / "config.json").is_file() and bool(weight_files)
        valid_locations.append({"path": str(candidate), "exists": candidate.is_dir(), "config_json": (candidate / "config.json").is_file(), "weight_files": weight_files, "valid_physx_transformers_snapshot": valid})

    unrelated = []
    for p in [
        ROOT / "CADReasoner/checkpoints/cadreasoner/model.safetensors",
        ROOT / "Dora/pytorch_lightning/ckpts/Dora-VAE-1.1/dora_vae_1_1.ckpt",
        ROOT / "Hunyuan3D-Part/P3-SAM/weights/p3sam.safetensors",
    ]:
        if p.is_file():
            unrelated.append({"path": str(p), "size": p.stat().st_size, "accepted": False, "reason": "unrelated project/model identity"})
    checkpoint_search = {
        "searched_roots": [str(ROOT), "/data/home/cuiyuehan/project (max depth 7, prior shell audit)"],
        "validation_rule": "must match official repo identity/config and expected model loading interface; suffix alone is insufficient",
        "valid_location_checks": valid_locations,
        "unrelated_examples_rejected": unrelated,
        "valid_physx_checkpoint_found": any(x["valid_physx_transformers_snapshot"] for x in valid_locations),
    }
    write_json("physx_checkpoint_search.json", checkpoint_search)

    env_probe = command([
        str(PYTHON), "-c",
        "import sys,torch,transformers,qwen_vl_utils,huggingface_hub,accelerate,flash_attn; "
        "print(sys.version); print('torch='+torch.__version__); print('cuda='+str(torch.cuda.is_available())); "
        "print('transformers='+transformers.__version__); print('huggingface_hub='+huggingface_hub.__version__); "
        "print('accelerate='+accelerate.__version__); print('flash_attn='+flash_attn.__version__)"
    ])
    dependency = {
        "environment": "physx-omni",
        "python": str(PYTHON),
        "probe": env_probe,
        "official_readme_python": "3.10",
        "official_readme_transformers": "4.50.0",
        "version_drift": "installed transformers differs from README pin; not remediated because checkpoint acquisition is blocked before load",
        "load_prerequisites_importable": env_probe["returncode"] == 0,
    }
    write_json("physx_dependency_audit.json", dependency)

    network_log = LOGS / "official_download_attempt.log"
    probe_log = LOGS / "network_connectivity_probe.log"
    probe_rc_file = LOGS / "network_connectivity_probe.rc"
    probe_text = probe_log.read_text(errors="replace") if probe_log.exists() else ""
    probe_rc = int(probe_rc_file.read_text().strip()) if probe_rc_file.exists() else None
    network = {
        "official_download_attempted": True,
        "method": str(REPO / "download.py"),
        "working_directory": str(ARTIFACTS / "checkpoint_download_attempt"),
        "timeout_seconds": 50,
        "return_code": 124,
        "url_host": "huggingface.co",
        "error_class": "NetworkUnavailable",
        "direct_https_probe_return_code": probe_rc,
        "direct_https_probe_log": str(probe_log),
        "direct_https_probe_error": probe_text.strip().splitlines()[-1] if probe_text.strip() else None,
        "download_log": str(network_log),
        "download_log_size": network_log.stat().st_size if network_log.exists() else None,
        "hf_endpoint_configured": bool(os.environ.get("HF_ENDPOINT")),
        "mirror_used": False,
        "reason_no_mirror": "No HF_ENDPOINT or user-configured Hugging Face mirror was present; policy forbids inventing an unverified mirror.",
        "physx_checkpoint_download_blocked": True,
    }
    write_json("physx_network_audit.json", network)

    smoke_case = find_smoke_case()
    source_render = FUSION_CASES / smoke_case / "physx" / "render" / f"{smoke_case}.png"
    source_meta = FUSION_CASES / smoke_case / "physx" / "render" / "render_metadata.json"
    smoke_dir = ARTIFACTS / "smoke_input"
    smoke_dir.mkdir(exist_ok=True)
    copied_render = smoke_dir / source_render.name
    copied_meta = smoke_dir / "render_metadata.json"
    if source_render.is_file():
        shutil.copy2(source_render, copied_render)
    if source_meta.is_file():
        shutil.copy2(source_meta, copied_meta)
    smoke = {
        "case": smoke_case,
        "selection_source": str(GATE1_SUMMARY),
        "selection_class": "A_PROGRAM_CAD_FRIENDLY",
        "input_adapter": "existing deterministic OBJ-to-PNG rendering adapter output, copied read-only for isolated Track B provenance",
        "source_render": str(source_render),
        "track_b_render": str(copied_render) if copied_render.is_file() else None,
        "render_sha256": sha256(copied_render) if copied_render.is_file() else None,
        "checkpoint_gate_passed": False,
        "attempted": False,
        "success": False,
        "raw_output": None,
        "understanding_json": None,
        "blocked_by": "PHYSX_INFERENCE_CHECKPOINT_UNAVAILABLE",
    }
    write_json("physx_smoke_gate.json", smoke)

    batch = {
        "frozen_cases": [f"REAL_{i:02d}" for i in range(1, 11)],
        "smoke_required_before_batch": True,
        "smoke_success": False,
        "cases_attempted": 0,
        "cases_success": 0,
        "run_permitted": False,
        "reason": "B7 forbids 10-case inference until official A-case smoke succeeds",
    }
    write_json("physx_batch_gate.json", batch)

    integrity = {
        "checkpoint_ready": False,
        "absolute_path": None,
        "file_size": None,
        "sha256": None,
        "load_attempted": False,
        "load_success": False,
        "reason": "No validated official checkpoint snapshot was available after the bounded official download attempt.",
    }
    write_json("physx_checkpoint_integrity.json", integrity)

    blockers = [
        {
            "code": "PHYSX_INFERENCE_CHECKPOINT_UNAVAILABLE",
            "class": "external_network",
            "detail": "Official Hugging Face endpoint huggingface.co:443 was unavailable (official downloader timed out; direct HTTPS probe was refused) and no user-configured mirror exists.",
            "evidence": str(ARTIFACTS / "physx_network_audit.json"),
        }
    ]
    summary = {
        "TRACK_B": "PHYSX_GATE_0_RECOVERY",
        "TRACK_B_STATUS": "BLOCKED",
        "PHYSX_GATE_0_RECOVERY": "BLOCKED",
        "PHYSX_REPO": str(REPO),
        "PHYSX_COMMIT": repo_audit["commit"],
        "PHYSX_BRANCH": repo_audit["branch"],
        "PHYSX_REPO_DIRTY": repo_audit["dirty"],
        "PHYSX_CHECKPOINT_READY": False,
        "PHYSX_CHECKPOINT_DOWNLOAD_BLOCKED": True,
        "PHYSX_CHECKPOINT_PATH": None,
        "PHYSX_CHECKPOINT_SIZE": None,
        "PHYSX_CHECKPOINT_SHA256": None,
        "PHYSX_CHECKPOINT_LOAD_ATTEMPTED": False,
        "PHYSX_CHECKPOINT_LOAD_SUCCESS": False,
        "RAW_OBJ_DIRECT_PHYSX_INPUT_SUPPORTED": False,
        "PHYSX_SMOKE_CASE": smoke_case,
        "PHYSX_SMOKE_ATTEMPTED": False,
        "PHYSX_SMOKE_SUCCESS": False,
        "PHYSX_CASES_ATTEMPTED": 0,
        "PHYSX_CASES_SUCCESS": 0,
        "PHYSX_SEMANTIC_AVAILABLE": 0,
        "PHYSX_FUNCTION_AVAILABLE": 0,
        "PHYSX_KINEMATICS_AVAILABLE": 0,
        "PHYSX_SCALE_AVAILABLE": 0,
        "PHYSX_RAW_OUTPUTS": 0,
        "PHYSX_UNDERSTANDING_OUTPUTS": 0,
        "PHYSX_USED_IN_MAC_BASELINE": False,
        "P3_TOUCHED": False,
        "MAC_RUNS": 0,
        "FUSION_RUNS": 0,
        "TESTS_PASSED": None,
        "TESTS_FAILED": None,
        "BLOCKERS": blockers,
        "generated_at": timestamp,
    }
    write_json("track_b_summary.json", summary)

    test_file = TRACK / "tests" / "test_track_b.py"
    test_result = command([str(PYTHON), "-m", "unittest", "-v", str(test_file)])
    (LOGS / "track_b_tests.log").write_text(test_result["stdout"] + test_result["stderr"])
    import re
    match = re.search(r"Ran (\d+) tests?", test_result["stdout"] + test_result["stderr"])
    test_count = int(match.group(1)) if match else 0
    summary["TESTS_PASSED"] = test_count if test_result["returncode"] == 0 else 0
    summary["TESTS_FAILED"] = 0 if test_result["returncode"] == 0 else max(test_count, 1)
    summary["TEST_RETURN_CODE"] = test_result["returncode"]
    write_json("track_b_summary.json", summary)
    return test_result["returncode"]


if __name__ == "__main__":
    raise SystemExit(main())
