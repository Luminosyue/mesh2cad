"""Plan provenance hashes."""
from __future__ import annotations

import hashlib
import json
from typing import Any

from design_plan.schema import REGISTRY_VERSION, RESOLVER_VERSION, VALIDATOR_VERSION


def dumps(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, default=str)


def sha(obj: Any) -> str:
    return hashlib.sha256(dumps(obj).encode()).hexdigest()


def file_sha(path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def provenance_record(plan: dict[str, Any], eligibility: dict[str, Any], catalog: dict[str, Any], source: str, model: str | None) -> dict[str, Any]:
    return {
        "QWEN_MODEL": model,
        "PLAN_SOURCE": source,
        "PLAN_HASH": sha(plan),
        "ALLOWED_BUILDERS": list(eligibility.get("ALLOWED_BUILDERS") or []),
        "MEASURED_SPEC_HASH": catalog.get("source_hash"),
        "PRIMITIVE_EVIDENCE_HASH": sha(eligibility.get("BUILDER_ELIGIBILITY")),
        "QWEN_OUTPUT_HASH": sha(plan) if source == "QWEN_PLAN" else None,
        "VALIDATOR_VERSION": VALIDATOR_VERSION,
        "RESOLVER_VERSION": RESOLVER_VERSION,
        "BUILDER_REGISTRY_VERSION": REGISTRY_VERSION,
    }
