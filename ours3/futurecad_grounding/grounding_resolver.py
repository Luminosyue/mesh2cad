from __future__ import annotations

from .deterministic_grounder import PrimitiveGroundingBackend


class StaleRuntimePrimitiveError(RuntimeError):
    pass


class GroundingResolver:
    def __init__(self, backend: PrimitiveGroundingBackend):
        self.backend = backend

    def ground(self, query, inventory, context=None):
        result = self.backend.ground(query, inventory, context or {})
        if result.valid:
            self.validate_runtime_ids(result.selected_runtime_ids, inventory)
        return result

    def validate_runtime_ids(self, runtime_ids, inventory) -> None:
        prefix = inventory.inventory_version + ':'
        for runtime_id in runtime_ids:
            if not runtime_id.startswith(prefix) or runtime_id not in inventory._shape_by_id:
                raise StaleRuntimePrimitiveError(f'STALE_RUNTIME_ID:{runtime_id}:{inventory.inventory_version}')

    def resolve_shapes(self, result, inventory):
        if not result.valid:
            raise RuntimeError(result.reject_reason or 'GROUNDING_INVALID')
        self.validate_runtime_ids(result.selected_runtime_ids, inventory)
        return [inventory.shape_for(runtime_id) for runtime_id in result.selected_runtime_ids]
