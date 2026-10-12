from __future__ import annotations

import re

REF = re.compile(r'^MEASURED_SPEC(\.[A-Za-z][A-Za-z0-9_]*)+$')


def validate_grounding_result(query, result, inventory) -> dict:
    reasons = []
    if result.inventory_version != inventory.inventory_version: reasons.append('STALE_RUNTIME_ID')
    if not result.valid: reasons.append(result.reject_reason or result.status)
    if result.valid and len(result.selected_runtime_ids) != query.expected_count: reasons.append('COUNT_MISMATCH')
    if any(not runtime_id.startswith(inventory.inventory_version + ':') for runtime_id in result.selected_runtime_ids): reasons.append('STALE_RUNTIME_ID')
    return {'GROUNDING_VALID': not reasons, 'reasons': reasons}


def validate_parameter_refs(parameter_refs: dict[str, str], catalog: dict) -> dict:
    reasons = []
    for name, ref in parameter_refs.items():
        if not isinstance(ref, str) or not REF.match(ref): reasons.append(f'BAD_PARAMETER_REF:{name}')
        elif ref not in catalog: reasons.append(f'PARAMETER_REF_NOT_FOUND:{ref}')
    return {'PARAMETER_REFS_VALID': not reasons, 'reasons': reasons}
