from __future__ import annotations

import hashlib
import json
from abc import ABC, abstractmethod
from typing import Any

from .schema import GroundingCandidate, GroundingResult, PrimitiveGroundingQuery
from .textual_query_parser import parse_query


class PrimitiveGroundingBackend(ABC):
    backend_name = 'ABSTRACT'

    @abstractmethod
    def ground(self, query, inventory, context=None) -> GroundingResult:
        raise NotImplementedError


class DeterministicBRepGrounder(PrimitiveGroundingBackend):
    backend_name = 'DETERMINISTIC_V1'

    def ground(self, query: PrimitiveGroundingQuery, inventory, context=None) -> GroundingResult:
        query_hash = hashlib.sha256(json.dumps(query.to_dict(), sort_keys=True).encode()).hexdigest()
        parsed = parse_query(query.natural_language_query)
        descriptors = inventory.descriptors(query.target_type)
        candidates = []
        geometry_conflict = False
        for descriptor in descriptors:
            hard_ok, scores, evidence, conflict = self._score(descriptor, query.structured_constraints, parsed)
            geometry_conflict = geometry_conflict or conflict
            if not hard_ok: continue
            total = 0.38 * scores['geometry'] + 0.24 * scores['position'] + 0.23 * scores['topology'] + 0.15 * scores['query']
            candidates.append(GroundingCandidate(descriptor['runtime_id'], scores['geometry'], scores['position'], scores['topology'], scores['query'], total, evidence))
        candidates.sort(key=lambda item: (-item.total_score, item.primitive_id))
        expected = int(query.expected_count)
        if not candidates:
            reason = 'GEOMETRY_CONSTRAINT_CONFLICT' if geometry_conflict else 'NO_MATCH'
            return GroundingResult(reason, self.backend_name, inventory.inventory_version, query_hash, [], [], 0.0, reason)
        if len(candidates) < expected:
            return GroundingResult('COUNT_MISMATCH', self.backend_name, inventory.inventory_version, query_hash, [], candidates, 0.0, 'COUNT_MISMATCH')
        selected = candidates[:expected]
        cutoff_margin = selected[-1].total_score - candidates[expected].total_score if len(candidates) > expected else 1.0
        confidence = min(1.0, 0.65 * sum(item.total_score for item in selected) / expected + 0.35 * max(cutoff_margin, 0.0))
        if len(candidates) > expected and cutoff_margin < 0.035:
            return GroundingResult('GROUNDING_AMBIGUOUS', self.backend_name, inventory.inventory_version, query_hash, [], candidates, confidence, 'AMBIGUOUS')
        if confidence < query.confidence_requirement:
            return GroundingResult('GROUNDING_AMBIGUOUS', self.backend_name, inventory.inventory_version, query_hash, [], candidates, confidence, 'LOW_CONFIDENCE')
        return GroundingResult('GROUNDING_VALID', self.backend_name, inventory.inventory_version, query_hash, [item.primitive_id for item in selected], candidates, confidence)

    def _score(self, descriptor: dict[str, Any], constraints: dict[str, Any], parsed: dict[str, Any]):
        evidence = []; hard_ok = True; conflict = False
        geometry_hits = position_hits = topology_hits = 0
        geometry_total = position_total = topology_total = 0

        def require(condition: bool, label: str, family: str):
            nonlocal hard_ok, conflict, geometry_hits, position_hits, topology_hits, geometry_total, position_total, topology_total
            if family == 'geometry': geometry_total += 1; geometry_hits += int(condition)
            elif family == 'position': position_total += 1; position_hits += int(condition)
            else: topology_total += 1; topology_hits += int(condition)
            if condition: evidence.append(label)
            else: hard_ok = False; conflict = True

        for key, raw in constraints.items():
            value = str(raw).upper() if not isinstance(raw, bool) else raw
            if key in {'count'}: continue
            if key == 'relative_position':
                values = [str(x).upper() for x in raw] if isinstance(raw, list) else [value]
                require(any(x in descriptor.get('relative_position', []) for x in values), 'relative_position', 'position')
            elif key == 'boundary_role':
                mapping = {'OUTER': 'outer_boundary', 'INNER': 'inner_boundary', 'SHARED': 'shared_trim', 'SEAM': 'seam'}
                require(bool(descriptor.get(mapping.get(value, ''), False)), f'boundary_role={value}', 'topology')
            elif key == 'orientation': require(value in descriptor.get('orientation', []), f'orientation={value}', 'geometry')
            elif key == 'curve_type': require(descriptor.get('curve_type') == value, f'curve_type={value}', 'geometry')
            elif key == 'surface_type': require(descriptor.get('surface_type') == value, f'surface_type={value}', 'geometry')
            elif key == 'closed': require(bool(descriptor.get('closed')) == bool(raw), 'closed', 'geometry')
            elif key == 'convexity': require(descriptor.get('convexity') == value, f'convexity={value}', 'topology')
            elif key == 'length_rank':
                condition = descriptor.get('length_rank') == 1 if value == 'LONGEST' else descriptor.get('length_percentile', 0.0) >= 0.70 if value == 'TOP' else descriptor.get('length_percentile', 1.0) <= 0.30
                require(condition, f'length_rank={value}', 'geometry')
            elif key == 'area_rank': require(descriptor.get('area_rank') == 1 if value == 'LARGEST' else True, f'area_rank={value}', 'geometry')
            elif key == 'adjacent_to': require(value in descriptor.get('adjacent_face_ids', []), 'adjacent_to', 'topology')
        query_hits = 0; query_total = 0
        for position in parsed['positions']:
            query_total += 1; query_hits += int(position in descriptor.get('relative_position', []))
        for token in parsed['geometry']:
            query_total += 1
            if token in {'VERTICAL', 'HORIZONTAL', 'LONGITUDINAL', 'TRANSVERSE'}: match = token in descriptor.get('orientation', [])
            elif token == 'CIRCULAR': match = descriptor.get('curve_type') == 'CIRCLE'
            elif token == 'STRAIGHT': match = descriptor.get('curve_type') == 'LINE'
            elif token in {'LONG', 'LONGEST'}: match = descriptor.get('length_percentile', 0.0) >= 0.70
            elif token in {'SHORT', 'SHORTEST'}: match = descriptor.get('length_percentile', 1.0) <= 0.30
            else: match = True
            query_hits += int(match)
        for token in parsed['topology']:
            query_total += 1
            match = descriptor.get({'OUTER':'outer_boundary','INNER':'inner_boundary','SHARED':'shared_trim','SEAM':'seam'}.get(token, ''), token == 'BOUNDARY' and not descriptor.get('seam'))
            query_hits += int(bool(match))
        scores = {
            'geometry': geometry_hits / max(geometry_total, 1) if geometry_total else 0.75,
            'position': position_hits / max(position_total, 1) if position_total else 0.70,
            'topology': topology_hits / max(topology_total, 1) if topology_total else 0.70,
            'query': query_hits / max(query_total, 1) if query_total else 0.65,
        }
        return hard_ok, scores, evidence, conflict
