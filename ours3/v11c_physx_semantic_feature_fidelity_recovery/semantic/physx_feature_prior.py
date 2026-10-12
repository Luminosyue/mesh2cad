from .semantic_role_schema import functional_role, normalize_role
from .semantic_geometry_compatibility import assess

def build_semantic_prior(raw_role, raw_confidence, descriptor, construction_prior, pattern_role=None, source='PHYSX_OR_QWEN_SEMANTIC_EVIDENCE'):
    role = normalize_role(raw_role)
    compatibility = assess(role, descriptor, pattern_role)
    accepted = float(raw_confidence or 0) >= .55 and compatibility['status'] != 'CONFLICT' and not role.startswith('UNKNOWN') and role != 'UNKNOWN'
    return {
        'semantic_role': role if accepted else ('UNKNOWN_TANK_PART' if 'TANK' in role else 'UNKNOWN'),
        'semantic_role_confidence': float(raw_confidence or 0), 'functional_role': functional_role(role),
        'pattern_role': pattern_role, 'geometry_expectations': compatibility['checks'],
        'geometry_compatibility': compatibility, 'cad_construction_prior': construction_prior,
        'PHYSX_RAW_ROLE': role, 'PHYSX_SEMANTIC_ROLE_ACCEPTED': accepted,
        'PHYSX_ROLE_USED_FOR_RANKING': accepted, 'evidence': {'source': source, 'geometry_authority': 'FROZEN_GEOMETRY_ANALYZER'},
    }
