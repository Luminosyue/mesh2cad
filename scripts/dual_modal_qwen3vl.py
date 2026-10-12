#!/usr/bin/env python3
"""Send dual-modal renders to the local Qwen3-VL server and record visual JSON for MAC."""

from __future__ import annotations

import argparse
import base64
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path("/data/home/cuiyuehan/project/mesh2cad")
MAC_ENV_FILE = ROOT / "ours3/.mac_env"
DEFAULT_BASE_URL = "http://127.0.0.1:18000/v1"
DEFAULT_MODEL = "Qwen3-VL-4B-Instruct"
IMAGE_NAMES = (
    "axonometric_shaded.png",
    "axonometric_render.png",
    "top_shaded.png",
    "side_shaded.png",
    "front_shaded.png",
)


def dump_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False, default=str) + "\n", encoding="utf-8")


def load_json(path: Path, default: Any = None) -> Any:
    if not path.is_file():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default


def load_mac_env(path: Path = MAC_ENV_FILE) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.is_file():
        return values
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("'\"")
    for key, value in values.items():
        os.environ.setdefault(key, value)
    os.environ.setdefault("VISUAL_BASE_URL", DEFAULT_BASE_URL)
    os.environ.setdefault("VISUAL_MODEL", DEFAULT_MODEL)
    os.environ.setdefault("VISUAL_API_KEY", "local")
    return values


def visual_base_url() -> str:
    load_mac_env()
    return os.environ.get("VISUAL_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def visual_root_url() -> str:
    base = visual_base_url()
    return base[: -3] if base.endswith("/v1") else base


def visual_model() -> str:
    load_mac_env()
    return os.environ.get("VISUAL_MODEL", DEFAULT_MODEL)


def healthcheck(timeout: float = 10.0) -> dict[str, Any]:
    base = visual_base_url()
    started = time.time()
    try:
        req = urllib.request.Request(visual_root_url() + "/health")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            payload = json.loads(resp.read())
        return {"ok": True, "base_url": base, "model": payload.get("model", visual_model()), "elapsed_seconds": time.time() - started, "raw": payload}
    except Exception as exc:
        return {"ok": False, "base_url": base, "model": visual_model(), "elapsed_seconds": time.time() - started, "error": f"{type(exc).__name__}: {exc}"}


def extract_json(text: str) -> Any:
    fenced = re.search(r"```(?:json)?\s*(.*?)```", text, flags=re.S | re.I)
    candidate = fenced.group(1) if fenced else text
    try:
        return json.loads(candidate)
    except Exception:
        pass
    start = min([pos for pos in (candidate.find("{"), candidate.find("[")) if pos >= 0], default=-1)
    end = max(candidate.rfind("}"), candidate.rfind("]"))
    if start < 0 or end <= start:
        raise ValueError("Qwen3-VL response did not contain JSON")
    return json.loads(candidate[start : end + 1])


def discover_dual_modal_dir(component_dir: Path) -> Path | None:
    for name in ("05_dual_modal", "dual_modal", "06_dual_modal_adapter"):
        path = component_dir / name
        if path.is_dir():
            return path
    return None


def discover_images(dual_dir: Path, max_images: int = 2) -> list[Path]:
    found: list[Path] = []
    seen: set[str] = set()
    for name in IMAGE_NAMES:
        path = dual_dir / name
        if path.is_file() and name not in seen:
            found.append(path)
            seen.add(name)
        if len(found) >= max_images:
            break
    if not found:
        found.extend(sorted(dual_dir.glob("*_shaded.png"))[:max_images])
    return found[:max_images]


def _image_part(path: Path) -> dict[str, Any]:
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return {"type": "image_url", "image_url": {"url": f"data:{mime};base64,{b64}"}}


def analyze_images(
    image_paths: list[Path],
    tokens_text: str = "",
    *,
    timeout: float = 180.0,
    max_tokens: int = 512,
) -> dict[str, Any]:
    health = healthcheck()
    if not health.get("ok"):
        return {
            "ok": False,
            "provider": "local_qwen3vl",
            "model": visual_model(),
            "base_url": visual_base_url(),
            "render_sent_as_image": False,
            "canonical_obj_sent_as_text": False,
            "images_sent": [],
            "parsed": None,
            "raw": None,
            "error": health.get("error") or "VISUAL_HEALTHCHECK_FAIL",
            "health": health,
        }
    images = [Path(path) for path in image_paths if Path(path).is_file()]
    if not images:
        return {
            "ok": False,
            "provider": "local_qwen3vl",
            "model": visual_model(),
            "base_url": visual_base_url(),
            "render_sent_as_image": False,
            "canonical_obj_sent_as_text": bool(tokens_text),
            "images_sent": [],
            "parsed": None,
            "raw": None,
            "error": "NO_DUAL_MODAL_IMAGE",
            "health": health,
        }
    prompt = (
        "Analyze this CAD component from the rendered view(s) and optional canonical OBJ tokens. "
        "Return strict JSON with keys: global_shape, visible_part_relationships, "
        "symmetry_or_pattern_evidence, likely_design_features, likely_builder_family, ambiguity. "
        "likely_builder_family must be one of PROFILE_LOFT, EXTRUSION, REVOLUTION, CYLINDER, BOX, FREEFORM. "
        "Do not estimate dimensions or coordinates; measurements are supplied separately.\n"
    )
    if tokens_text.strip():
        prompt += "Canonical OBJ / part tokens:\n" + tokens_text.strip()[:4000]
    content: list[dict[str, Any]] = [{"type": "text", "text": prompt}]
    content.extend(_image_part(path) for path in images)
    payload = {
        "model": visual_model(),
        "temperature": 0.0,
        "max_tokens": max_tokens,
        "messages": [{"role": "user", "content": content}],
    }
    req = urllib.request.Request(
        visual_base_url() + "/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {os.environ.get('VISUAL_API_KEY', 'local')}"},
        method="POST",
    )
    started = time.time()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
    except Exception as exc:
        return {
            "ok": False,
            "provider": "local_qwen3vl",
            "model": visual_model(),
            "base_url": visual_base_url(),
            "render_sent_as_image": True,
            "canonical_obj_sent_as_text": bool(tokens_text.strip()),
            "images_sent": [str(path) for path in images],
            "parsed": None,
            "raw": None,
            "error": f"{type(exc).__name__}: {exc}",
            "elapsed_seconds": time.time() - started,
            "health": health,
        }
    raw = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
    try:
        parsed = extract_json(raw)
    except Exception:
        parsed = {
            "global_shape": raw,
            "visible_part_relationships": [],
            "symmetry_or_pattern_evidence": {},
            "likely_design_features": [],
            "likely_builder_family": "FREEFORM",
            "ambiguity": "VLM_FREE_TEXT",
        }
    return {
        "ok": True,
        "provider": "local_qwen3vl",
        "model": data.get("model") or visual_model(),
        "base_url": visual_base_url(),
        "render_sent_as_image": True,
        "canonical_obj_sent_as_text": bool(tokens_text.strip()),
        "images_sent": [str(path.resolve()) for path in images],
        "image_sha256": {path.name: __import__("hashlib").sha256(path.read_bytes()).hexdigest() for path in images},
        "parsed": parsed,
        "raw": raw,
        "usage": data.get("usage") or {},
        "elapsed_seconds": time.time() - started,
        "health": health,
    }


def analyze_dual_modal_dir(dual_dir: Path, *, max_images: int = 2, force: bool = False) -> dict[str, Any]:
    dual_dir = Path(dual_dir)
    out_path = dual_dir / "visual_context.json"
    if out_path.is_file() and not force:
        existing = load_json(out_path, {}) or {}
        if existing.get("ok") and existing.get("render_sent_as_image"):
            return existing
    images = discover_images(dual_dir, max_images=max_images)
    token_path = dual_dir / "canonical_obj_tokens.txt"
    tokens = token_path.read_text(encoding="utf-8", errors="replace") if token_path.is_file() else ""
    result = analyze_images(images, tokens)
    result["dual_modal_dir"] = str(dual_dir.resolve())
    dump_json(out_path, result)
    manifest_path = dual_dir / "mac_input_manifest.json"
    manifest = load_json(manifest_path, {}) or {}
    manifest.update(
        {
            "visual_context": str(out_path.resolve()),
            "VISUAL_MODEL": result.get("model"),
            "VISUAL_BASE_URL": result.get("base_url"),
            "VISUAL_QWEN3VL_OK": bool(result.get("ok")),
            "render_sent_as_image": bool(result.get("render_sent_as_image") and result.get("ok")),
            "DUAL_MODAL_ACTUALLY_USED_BY_MAC": bool(manifest.get("DUAL_MODAL_ACTUALLY_USED_BY_MAC") and result.get("ok")),
        }
    )
    dump_json(manifest_path, manifest)
    return result


def visual_json_for_mac(component_dir: Path) -> dict[str, Any] | None:
    dual = discover_dual_modal_dir(Path(component_dir))
    if dual is None:
        return None
    payload = load_json(dual / "visual_context.json")
    if not isinstance(payload, dict) or not payload.get("ok"):
        payload = analyze_dual_modal_dir(dual)
    parsed = payload.get("parsed") if isinstance(payload, dict) else None
    if not payload.get("ok") or not parsed:
        return None
    return parsed


def mark_visual_entered_mac(component_dir: Path, entered: bool) -> None:
    dual = discover_dual_modal_dir(Path(component_dir))
    if dual is None:
        return
    manifest_path = dual / "mac_input_manifest.json"
    manifest = load_json(manifest_path, {}) or {}
    visual = load_json(dual / "visual_context.json", {}) or {}
    manifest["DUAL_MODAL_ACTUALLY_USED_BY_MAC"] = bool(entered and visual.get("ok") and visual.get("render_sent_as_image"))
    manifest["VISUAL_ENTERED_MAC_PROMPT"] = bool(entered)
    dump_json(manifest_path, manifest)


def canary_text_mac(component_dir: Path) -> dict[str, Any]:
    """Send Qwen3-VL JSON into the text MAC architect so images affect CAD planning."""
    load_mac_env()
    component_dir = Path(component_dir)
    parsed = visual_json_for_mac(component_dir)
    if parsed is None:
        raise RuntimeError(f"CANARY_VISUAL_MISSING:{component_dir}")
    mac_root = ROOT / "Multi-Agent-CAD"
    if str(mac_root) not in sys.path:
        sys.path.insert(0, str(mac_root))
    from multi_agent_cad import config
    import multi_agent_cad.nodes as mac_nodes

    client = mac_nodes._llm_client()
    model = os.environ.get("TEXT_MODEL") or config.ARCHITECT_MODEL
    started = time.time()
    response = client.chat.completions.create(
        model=model,
        temperature=0,
        max_tokens=800,
        messages=[
            {
                "role": "system",
                "content": (
                    "Return JSON only. You are the CAD architect. Cite Qwen3-VL global_shape in cad_brief. "
                    "Never invent dimensions. Runtime will reread source mesh."
                ),
            },
            {
                "role": "user",
                "content": (
                    "Use this Qwen3-VL visual JSON (images were sent to local Qwen3-VL-4B-Instruct) "
                    "to choose HOW to build. JSON:\n"
                    + json.dumps(parsed, ensure_ascii=False)
                ),
            },
        ],
    )
    raw = response.choices[0].message.content or ""
    mark_visual_entered_mac(component_dir, True)
    result = {
        "ok": True,
        "component_id": component_dir.name,
        "component_dir": str(component_dir),
        "text_model": model,
        "visual_model": visual_model(),
        "visual_parsed": parsed,
        "mac_raw": raw,
        "elapsed_seconds": time.time() - started,
        "usage": {
            "prompt_tokens": getattr(response.usage, "prompt_tokens", None),
            "completion_tokens": getattr(response.usage, "completion_tokens", None),
        },
    }
    if (component_dir / "06_mac").is_dir():
        dump_json(component_dir / "06_mac" / "visual_mac_canary.json", result)
    if (component_dir / "mac").is_dir():
        dump_json(component_dir / "mac" / "visual_mac_canary.json", result)
    dump_json(ROOT / "ours3/dual_modal_qwen3vl_wireup_v1/artifacts" / f"{component_dir.name}_visual_mac_canary.json", result)
    return result


def apply_existing(roots: list[Path], *, max_images: int = 2, force: bool = False) -> dict[str, Any]:
    rows = []
    for root in roots:
        for component_dir in sorted(Path(root).glob("03_components/P3_COMPONENT_*")):
            dual = discover_dual_modal_dir(component_dir)
            if dual is None:
                continue
            result = analyze_dual_modal_dir(dual, max_images=max_images, force=force)
            rows.append(
                {
                    "root": str(Path(root).name),
                    "component_id": component_dir.name,
                    "ok": bool(result.get("ok")),
                    "elapsed_seconds": result.get("elapsed_seconds"),
                    "images_sent": result.get("images_sent"),
                    "global_shape": (result.get("parsed") or {}).get("global_shape") if isinstance(result.get("parsed"), dict) else None,
                    "likely_builder_family": (result.get("parsed") or {}).get("likely_builder_family") if isinstance(result.get("parsed"), dict) else None,
                    "error": result.get("error"),
                }
            )
            print(component_dir.name, "OK" if result.get("ok") else "FAIL", rows[-1].get("global_shape") or rows[-1].get("error"), flush=True)
    summary = {
        "ok_count": sum(row["ok"] for row in rows),
        "fail_count": sum(not row["ok"] for row in rows),
        "component_count": len(rows),
        "model": visual_model(),
        "base_url": visual_base_url(),
        "rows": rows,
    }
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Wire dual-modal renders into local Qwen3-VL")
    parser.add_argument("--health", action="store_true")
    parser.add_argument("--apply-existing", action="store_true")
    parser.add_argument("--force", action="store_true")
    parser.add_argument("--max-images", type=int, default=2)
    parser.add_argument("--dual-dir", type=Path)
    args = parser.parse_args()
    load_mac_env()
    if args.health or (not args.apply_existing and args.dual_dir is None):
        health = healthcheck()
        print(json.dumps(health, indent=2, ensure_ascii=False))
        if not health.get("ok"):
            raise SystemExit(2)
        if not args.apply_existing and args.dual_dir is None:
            return
    if args.dual_dir is not None:
        result = analyze_dual_modal_dir(args.dual_dir, max_images=args.max_images, force=args.force)
        print(json.dumps({k: result.get(k) for k in ("ok", "model", "images_sent", "parsed", "error", "elapsed_seconds")}, indent=2, ensure_ascii=False, default=str))
        raise SystemExit(0 if result.get("ok") else 1)
    if args.apply_existing:
        roots = [
            ROOT / "ours3/build_a_robot_pipeline_a_fullstack_repair_v2",
            ROOT / "ours3/tank_p3_45_component_pipeline_a_fullrun_v5",
        ]
        summary = apply_existing(roots, max_images=args.max_images, force=args.force)
        out = ROOT / "ours3/dual_modal_qwen3vl_wireup_v1/artifacts/visual_backfill_summary.json"
        dump_json(out, summary)
        print(f"ok={summary['ok_count']} fail={summary['fail_count']} wrote={out}")
        if summary["fail_count"] == 0:
            canaries = [
                ROOT / "ours3/build_a_robot_pipeline_a_fullstack_repair_v2/03_components/P3_COMPONENT_001",
                ROOT / "ours3/tank_p3_45_component_pipeline_a_fullrun_v5/03_components/P3_COMPONENT_000",
            ]
            canary_rows = []
            for path in canaries:
                canary_rows.append(canary_text_mac(path))
                print("CANARY", path.name, "ok", flush=True)
            dump_json(ROOT / "ours3/dual_modal_qwen3vl_wireup_v1/artifacts/visual_mac_canary_summary.json", {"rows": canary_rows})
        raise SystemExit(0 if summary["fail_count"] == 0 else 1)


if __name__ == "__main__":
    main()
