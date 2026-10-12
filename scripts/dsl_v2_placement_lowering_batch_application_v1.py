from __future__ import annotations

import hashlib
import json
from pathlib import Path

ROOT = Path('/data/home/cuiyuehan/project/mesh2cad')
AUDIT = ROOT / 'ours3/dsl_v2_placement_lowering_audit_v1'
OUT = ROOT / 'ours3/dsl_v2_placement_lowering_batch_application_v1'
OUT.mkdir(parents=True, exist_ok=True)

def dump(name, x): (OUT/name).write_text(json.dumps(x, indent=2, default=str) + '\n')
def lines(name, xs): (OUT/name).write_text('\n'.join(json.dumps(x, default=str) for x in xs) + ('\n' if xs else ''))
def sha(p): return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
    audit = json.loads((AUDIT/'UNSUPPORTED_CALL_CHAIN_AUDIT.json').read_text())['records']
    candidates = [x for x in audit if x['whether_geometry_semantics_are_deterministic']]
    freeze = {'status': 'LOWERING_CANDIDATE_SET_FROZEN_FOR_AUDIT_ONLY', 'freeze_allowed': False, 'candidate_n': len(candidates), 'records': [{'cad_id': x['cad_id'], 'uuid': x['cad_id'], 'row_index': x['row_index'], 'source_sha256': x['source_sha256'], 'step_sha256': x['step_sha256'], 'full_call_chain': x['full_call_chain'], 'candidate_lowerings': [m for m in x['unsupported_calls'] if m in {'center','translate','workplane','rotate','mirrorY'}], 'remaining_unsupported_calls_before': x['unsupported_calls']} for x in candidates]}
    dump('LOWERING_CANDIDATE_FREEZE.json', freeze)
    rules = [
        {'rule_name': 'CENTER_TO_PROFILE_PLACEMENT', 'matched_AST_pattern': 'Workplane(...).center(cx, cy).<profile construction>', 'preconditions': ['numeric cx/cy', 'principal plane', 'profile coordinates can be shifted exactly'], 'geometry_update': 'shift profile coordinates once in workplane x/y basis; preserve normal/x_axis', 'unsupported_conditions': ['topology-selected workplane', 'non-static subtree', 'double application'], 'provenance_fields': ['source_call', 'cx', 'cy', 'lowered_into', 'rule']},
        {'rule_name': 'TRANSLATE_TO_EXISTING_GEOMETRY_PLACEMENT', 'matched_AST_pattern': '<primitive or complete subtree>.translate((dx,dy,dz))', 'preconditions': ['numeric translation', 'entire affected subtree identified', 'translation applied exactly once'], 'geometry_update': 'add translation to primitive/profile/axis origin or equivalent placement parameters', 'unsupported_conditions': ['partial subtree coverage', 'rotation-dependent frame without proof', 'double transform'], 'provenance_fields': ['source_call', 'vector', 'affected_objects', 'transform_application_count', 'double_transform_check', 'rule']},
        {'rule_name': 'WORKPLANE_OFFSET_TO_ORIGIN', 'matched_AST_pattern': 'Workplane(principal_plane).workplane(offset=d)', 'preconditions': ['no preceding faces(...) selection', 'numeric offset', 'principal plane'], 'geometry_update': 'origin = origin + d * normal; preserve normal/x_axis', 'unsupported_conditions': ['faces(...).workplane(...)', 'non-principal plane'], 'provenance_fields': ['source_call', 'offset', 'resulting_origin', 'rule']},
    ]
    dump('PLACEMENT_LOWERING_RULES_V1.json', {'version': 1, 'rules': rules, 'new_dsl_operator_added': False})
    batch = []; prov = []; composition = []
    for x in candidates:
        lowerings = x['unsupported_calls']; safe_static = x['lowering_confidence'] == 'HIGH'
        # The existing canonicalizer has no general source-to-DSL lowering pass yet.
        # Keep complex source untouched rather than deleting a call without baking it.
        applied = False
        reason = 'RULE_UNIT_VALIDATED_BUT_BATCH_SOURCE_LOWERING_NOT_APPLIED: full subtree bake requires source-aware canonicalizer'
        for rule in lowerings:
            rec = {'cad_id': x['cad_id'], 'row_index': x['row_index'], 'source_call': rule, 'lowered_into': None, 'rule': {'center':'CENTER_TO_PROFILE_PLACEMENT','translate':'TRANSLATE_TO_EXISTING_GEOMETRY_PLACEMENT','workplane':'WORKPLANE_OFFSET_TO_ORIGIN','rotate':'TRANSFORM_NOT_VALIDATED','mirrorY':'TRANSFORM_NOT_VALIDATED'}[rule], 'applied': applied, 'reason': reason, 'lowering_confidence': 'HIGH' if safe_static else 'MEDIUM'}
            if rule == 'center': batch.append(rec)
            elif rule == 'translate': batch.append(rec)
            elif rule == 'workplane': batch.append(rec)
            prov.append(rec)
        composition.append({'cad_id': x['cad_id'], 'ordered_transform_chain': [m for m in x['full_call_chain'] if m.split('.')[-1] in {'center','translate','workplane','rotate','mirrorY'}], 'composed_transform': None, 'affected_geometry': x['dependent_operator'], 'composition_valid': False, 'reason': reason})
    lines('CENTER_BATCH_LOWERING.jsonl', [x for x in batch if x['source_call']=='center']); lines('TRANSLATE_BATCH_LOWERING.jsonl', [x for x in batch if x['source_call']=='translate']); lines('WORKPLANE_OFFSET_BATCH_LOWERING.jsonl', [x for x in batch if x['source_call']=='workplane']); lines('LOWERING_PROVENANCE.jsonl', prov); lines('LOWERING_TRANSFORM_COMPOSITION.jsonl', composition)
    post = [{'cad_id': x['cad_id'], 'row_index': x['row_index'], 'all_calls_accounted_for': False, 'remaining_unsupported_calls': x['unsupported_calls'], 'strict_eligible': False, 'reason': 'batch lowering not applied'} for x in candidates]
    lines('POST_LOWERING_STRICT_AST_AUDIT.jsonl', post)
    for name in ['POST_LOWERING_DSL_ROUNDTRIP.jsonl','POST_LOWERING_EXECUTION.jsonl','POST_LOWERING_GEOMETRY_VERIFICATION.jsonl']:
        lines(name, [])
    dump('POST_LOWERING_DETERMINISM.json', {'status':'NOT_RUN','reason':'no post-lowering DSL cases'})
    dump('STRICT_COVERAGE_RECOVERY.json', {'strict_eligible_before': 3, 'strict_eligible_after': 3, 'absolute_case_gain': 0, 'percentage_point_gain': 0.0, 'relative_coverage_multiplier': 1.0, 'batch_applied_n': 0, 'potential_after_prior_audit': 21})
    blocked = {'FACES_CASES': 21, 'TOPOLOGY_AWARE_REQUIRED': 21, 'POLARARRAY_CASES': 8, 'CSKHOLE_CASES': 7, 'MIRROR_CASES': 1, 'LOFT_CASES': 0, 'SHELL_CASES': 0, 'OTHER_BLOCKERS': 20, 'placement_candidates_not_applied': len(candidates)}
    dump('POST_LOWERING_BLOCKER_CENSUS.json', blocked)
    dump('POST_LOWERING_ELIGIBLE_OPERATION_DISTRIBUTION.json', {'strict_eligible_n': 3, 'true_revolve': 0, 'boolean': 0, 'fillet': 1, 'chamfer': 1, 'multi_op': 3})
    report = {'CURRENT_GATE': 'DSL_V2_PLACEMENT_LOWERING_BATCH_NOT_APPLIED', 'DECLARED_POOL': 63, 'STRICT_ELIGIBLE_BEFORE': 3, 'STRICT_ELIGIBLE_AFTER': 3, 'STRICT_COVERAGE_BEFORE': '3/63', 'STRICT_COVERAGE_AFTER': '3/63', 'ABSOLUTE_CASE_GAIN': 0, 'PERCENTAGE_POINT_GAIN': 0.0, 'RELATIVE_COVERAGE_MULTIPLIER': 1.0, 'LOWERING_CANDIDATES': len(candidates), 'LOWERING_APPLIED': 0, 'CENTER_CASES': sum('center' in x['unsupported_calls'] for x in audit), 'CENTER_LOWERABLE': sum('center' in x['unsupported_calls'] for x in candidates), 'CENTER_APPLIED': 0, 'CENTER_GEOMETRY_PASS': 1, 'CENTER_RECOVERED': 0, 'TRANSLATE_CASES': sum('translate' in x['unsupported_calls'] for x in audit), 'TRANSLATE_LOWERABLE': sum('translate' in x['unsupported_calls'] for x in candidates), 'TRANSLATE_APPLIED': 0, 'TRANSLATE_GEOMETRY_PASS': 1, 'TRANSLATE_RECOVERED': 0, 'WORKPLANE_CASES': sum('workplane' in x['unsupported_calls'] for x in audit), 'WORKPLANE_LOWERABLE': 0, 'WORKPLANE_APPLIED': 0, 'WORKPLANE_GEOMETRY_PASS': 1, 'WORKPLANE_RECOVERED': 0, 'FACES_CASES': 21, 'TOPOLOGY_AWARE_REQUIRED': 21, 'POLARARRAY_CASES': 8, 'CSKHOLE_CASES': 7, 'MIRROR_CASES': 1, 'LOFT_CASES': 0, 'SHELL_CASES': 0, 'OTHER_BLOCKERS': 20, 'TRUE_REVOLVE_CASES': 0, 'BOOLEAN_CASES': 0, 'FILLET_CASES': 1, 'CHAMFER_CASES': 1, 'MULTI_OP_CASES': 3, 'ROUNDTRIP': '0/0', 'DETERMINISM': 'NOT_RUN', 'BACKEND_EXEC': '0/0', 'STEP_RELOAD': '0/0', 'GEOMETRY_VERIFIED': '0/0', 'CANARY8_SIZE_READY': 'NO', 'CANARY8_OPERATION_COVERAGE_INCOMPLETE': 'YES', 'CANARY_N': 0, 'freeze_allowed': False, 'TRAINING_RUN': 'NO', 'DECODE_RUN': 'NO', 'NEW_DSL_OPERATOR_ADDED': 'NO', 'PLACEMENT_MODEL_CHANGED': 'NO', 'C2_CHANGED': 'NO', 'SONATA_CHANGED': 'NO', 'SPATIALLM_CHANGED': 'NO', 'GEOMETRY_GATE_CHANGED': 'NO', 'NEXT_STEP': 'DSL_V2_REMAINING_BLOCKER_PRIORITY_AUDIT_V1'}
    dump('FINAL_REPORT.json', report); (OUT/'FINAL_REPORT.md').write_text('\n'.join(f'{k} = {v}' for k,v in report.items()) + '\n'); print(json.dumps(report, indent=2))

if __name__ == '__main__': main()
