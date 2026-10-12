import numpy as np

def source_proxy_metrics(descriptor, builder, role, pattern_role=None):
    bbox_proxy = builder in {'EXTRUSION','PLANE'} and descriptor['section_variation']>.10 and role in {'HULL','FUSELAGE','MAIN_WING','TAILPLANE','TURRET'}
    circular_fail = role in {'ROAD_WHEEL','GUN_BARREL','SHAFT'} and builder not in {'CYLINDER','REVOLUTION'}
    pattern_fail = bool(pattern_role and builder=='EXTRUSION')
    safe_low = bbox_proxy or circular_fail or pattern_fail
    return {'BBOX_PROXY_RECONSTRUCTION':bbox_proxy,'CIRCULAR_FEATURE_FIDELITY_FAIL':circular_fail,
            'PATTERN_FIDELITY_FAIL':pattern_fail,'SAFE_BUT_LOW_FIDELITY':safe_low,
            'FIDELITY_QA_PASS':not safe_low,'measurement_source':'SOURCE_DESCRIPTOR_PLUS_CANDIDATE_FAMILY'}
