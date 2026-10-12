from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any


def stable_hash(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode()).hexdigest()


@dataclass
class GroundingProvenanceLog:
    records: list[dict[str, Any]] = field(default_factory=list)

    def append(self, *, inventory, query, result, feature_operation=None, result_shape_signature=None):
        candidate_by_id = {item.primitive_id: item for item in result.ranked_candidates}
        for runtime_id in result.selected_runtime_ids or [None]:
            descriptor = next((row for row in inventory.descriptors(query.target_type) if row['runtime_id'] == runtime_id), None)
            candidate = candidate_by_id.get(runtime_id)
            self.records.append({
                'shape_signature': inventory.shape_signature,
                'inventory_hash': inventory.inventory_hash,
                'inventory_version': inventory.inventory_version,
                'query_hash': result.query_hash,
                'query': query.to_dict(),
                'selected_runtime_id': runtime_id,
                'selected_geometry_signature': stable_hash(descriptor) if descriptor else None,
                'score': candidate.total_score if candidate else None,
                'confidence': result.confidence,
                'status': result.status,
                'feature_operation': feature_operation,
                'result_shape_signature': result_shape_signature,
            })

    def to_dict(self):
        return {'schema': 'GroundingProvenanceV1', 'records': self.records}
