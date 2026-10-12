from __future__ import annotations

from .schema import FeatureOperationPlan, FutureCADProgramProposal, PrimitiveGroundingQuery


class FutureCADToV11Adapter:
    """Schema adapter only; it does not call or impersonate FutureCAD."""

    def adapt(self, proposal: FutureCADProgramProposal) -> list[FeatureOperationPlan]:
        plans = []
        query_by_id = {item['query_id']: item for item in proposal.grounding_queries}
        for index, feature in enumerate(proposal.base_feature_sequence):
            operation = feature['operation'].upper()
            if operation not in {'FILLET', 'CHAMFER', 'SHELL'}:
                continue
            raw_query = query_by_id[feature['grounding_query_id']]
            query = PrimitiveGroundingQuery(
                target_type=raw_query['target_type'],
                natural_language_query=raw_query['natural_language_query'],
                structured_constraints=raw_query.get('structured_constraints') or {},
                expected_count=int(raw_query.get('expected_count', 1)),
                selection_mode=raw_query.get('selection_mode', 'EXACT_COUNT'),
                confidence_requirement=float(raw_query.get('confidence_requirement', 0.60)),
            )
            refs = {}
            for parameter_name, placeholder in feature.get('numeric_parameter_placeholders', {}).items():
                if placeholder not in proposal.numeric_parameter_placeholders:
                    raise ValueError(f'PARAMETER_PLACEHOLDER_NOT_FOUND:{placeholder}')
                refs[parameter_name] = proposal.numeric_parameter_placeholders[placeholder]
            plans.append(FeatureOperationPlan(operation, query, refs, feature.get('operation_id') or f'FEATURE_{index:03d}', bool(feature.get('diagnostic_only', False))))
        return plans
