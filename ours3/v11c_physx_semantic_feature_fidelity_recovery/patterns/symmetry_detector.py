import numpy as np

def detect_symmetries(parts):
    if len(parts)<2:return []
    center=np.mean([p['descriptor']['centroid'] for p in parts],axis=0); pairs=[]; used=set()
    for p in parts:
        if p['part_id'] in used:continue
        c=np.asarray(p['descriptor']['centroid']); best=None
        for axis in range(3):
            target=c.copy();target[axis]=2*center[axis]-target[axis]
            for q in parts:
                if q['part_id']==p['part_id'] or q['part_id'] in used:continue
                error=np.linalg.norm(np.asarray(q['descriptor']['centroid'])-target)
                shape=np.linalg.norm(np.sort(p['descriptor']['extents'])-np.sort(q['descriptor']['extents']))
                score=error+shape
                if best is None or score<best[0]:best=(score,axis,q)
        if best and best[0]<.12:
            pairs.append((p['part_id'],best[2]['part_id']));used|={p['part_id'],best[2]['part_id']}
    return [{'symmetry_id':'SYMMETRY_000','pairs':pairs,'transform':{'type':'MIRROR','plane_origin':center.tolist()},'measurement_source':'DETERMINISTIC_GEOMETRY'}] if pairs else []
