import numpy as np

def build_relation_graph(parts, patterns, symmetries):
    relations = []
    if not parts:
        return {'nodes': [], 'relations': []}
    root = max(parts, key=lambda p: p['descriptor']['area'])['part_id']
    for part in parts:
        if part['part_id'] != root:
            relations.append({'source':part['part_id'],'target':root,'type':'ATTACHED_TO','evidence':'BBOX_DISTANCE_AND_AREA_CENTRALITY'})
    for pattern in patterns:
        for member in pattern['members'][1:]:
            relations.append({'source':member,'target':pattern['prototype_part'],'type':'REPEATED_WITH','evidence':'DETERMINISTIC_DESCRIPTOR_AND_SPACING'})
    for group in symmetries:
        for a,b in group['pairs']:
            relations.append({'source':a,'target':b,'type':'SYMMETRIC_WITH','evidence':'DETERMINISTIC_MIRROR_TRANSFORM'})
    return {'root':root,'nodes':[p['part_id'] for p in parts],'relations':relations}
