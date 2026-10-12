import itertools
import numpy as np

def _shape_vector(part):
    d=part['descriptor']; e=np.sort(np.asarray(d['extents'],float))[::-1]; return e/max(e[0],1e-12)

def detect_patterns(parts, global_category):
    unused=set(p['part_id'] for p in parts); by={p['part_id']:p for p in parts}; groups=[]
    while unused:
        seed=unused.pop(); sv=_shape_vector(by[seed]); members=[seed]
        for other in list(unused):
            if np.linalg.norm(_shape_vector(by[other])-sv) < .38:
                members.append(other);unused.remove(other)
        if len(members)<3: continue
        centers=np.asarray([by[x]['descriptor']['centroid'] for x in members]); _,s,vh=np.linalg.svd(centers-centers.mean(0),full_matrices=False)
        direction=vh[0]; coordinates=np.sort((centers-centers.mean(0))@direction); spacing=np.diff(coordinates)
        regularity=float(np.std(spacing)/max(np.mean(np.abs(spacing)),1e-12)) if len(spacing) else 1
        disc=float(np.mean([by[x]['descriptor']['disc_likeness'] for x in members]))
        role='ROAD_WHEEL_PATTERN' if 'TANK' in global_category and disc>.35 else 'REPEATED_ELEMENT_PATTERN'
        groups.append({'pattern_id':f'PATTERN_{len(groups):03d}','semantic_role':role,'prototype_part':members[0],
                       'members':sorted(members),'count':len(members),'direction_ref':direction.tolist(),
                       'spacing_refs':spacing.tolist(),'spacing_regularity_cv':regularity,'disc_likeness':disc,
                       'confidence':float(max(0,min(1,.65+.2*disc-.2*regularity))),
                       'measurement_source':'GEOMETRY_ANALYZER_DESCRIPTORS'})
    return groups
