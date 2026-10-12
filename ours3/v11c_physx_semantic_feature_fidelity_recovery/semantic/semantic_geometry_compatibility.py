import numpy as np

def geometry_descriptor(mesh, node):
    vertices = np.asarray(mesh.vertices, float)
    centered = vertices - vertices.mean(0)
    values, vectors = np.linalg.eigh(np.cov(vertices.T))
    order = np.argsort(values)[::-1]
    values, vectors = values[order], vectors[:, order]
    extents = np.ptp(vertices, axis=0)
    sorted_extents = np.sort(extents)[::-1]
    pca = values / max(values[0], 1e-12)
    axis = vectors[:, 0]
    radial = np.linalg.norm(centered - np.outer(centered @ axis, axis), axis=1)
    section_bins = np.linspace((centered @ axis).min(), (centered @ axis).max(), 9)
    widths = []
    for lo, hi in zip(section_bins[:-1], section_bins[1:]):
        keep = ((centered @ axis) >= lo) & ((centered @ axis) <= hi)
        if keep.sum() > 20:
            widths.append(float(np.ptp(vertices[keep], axis=0).sum()))
    section_variation = float(np.std(widths) / max(np.mean(widths), 1e-12)) if widths else 0.0
    return {
        'centroid': np.asarray(mesh.centroid, float).tolist(), 'extents': extents.tolist(),
        'sorted_extent_ratios': (sorted_extents / max(sorted_extents[0], 1e-12)).tolist(),
        'principal_values': values.tolist(), 'principal_value_ratios': pca.tolist(),
        'principal_axes': vectors.T.tolist(), 'radial_cv': float(np.std(radial) / max(np.mean(radial), 1e-12)),
        'disc_likeness': float(min(pca[1] / max(pca[0], 1e-12), 1.0) * (1.0 - min(pca[2] / max(pca[1], 1e-12), 1.0))),
        'rod_likeness': float(1.0 - min(pca[1], 1.0)), 'planarity': float(1.0 - min(pca[2] / max(pca[1], 1e-12), 1.0)),
        'section_variation': section_variation, 'area': float(mesh.area),
        'geometry_class': node.get('geometry_role') or node.get('geometry_class'),
        'measurement_source': 'FROZEN_GEOMETRY_ANALYZER_PART_MESH',
    }

def assess(role, descriptor, pattern_role=None):
    disc, rod, planar = descriptor['disc_likeness'], descriptor['rod_likeness'], descriptor['planarity']
    checks = []
    if role in {'ROAD_WHEEL','DRIVE_SPROCKET','IDLER_WHEEL'}:
        score = max(disc, 0.9 if pattern_role == 'ROAD_WHEEL_PATTERN' else 0.0); checks += ['disc_likeness','repetition']
    elif role in {'GUN_BARREL','SHAFT','CYLINDRICAL_PART'}:
        score = rod; checks += ['rod_likeness','axis_consistency']
    elif role in {'MAIN_WING','TAILPLANE','VERTICAL_TAIL','WALL','ROOF','PLATE','ARMOR_PLATE'}:
        score = max(planar, 0.55); checks += ['planarity','section_variation']
    elif role in {'HULL','FUSELAGE','TURRET','SHELL','FREEFORM_SKIN','TRACK'}:
        score = 0.75; checks += ['global_support','shape_complexity']
    elif role.startswith('UNKNOWN') or role == 'UNKNOWN':
        return {'status':'UNKNOWN','score':0.0,'checks':[]}
    else:
        score = 0.5; checks += ['generic_geometry']
    status = 'SUPPORTED' if score >= .62 else ('WEAKLY_SUPPORTED' if score >= .38 else 'CONFLICT')
    return {'status':status,'score':float(score),'checks':checks}
