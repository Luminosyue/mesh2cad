"""V2 evaluator core; V1 metric definitions retained, with explicit in-memory adapters."""
import hashlib
import numpy as np
import cadquery as cq
from scipy.spatial import cKDTree
from coordinate_adapter.coordinate_adapter import adapt_shape

GLOBAL_SEED = 20260915
SURFACE_SAMPLE_N = 10000

def stable_seed(case_id):
    return int.from_bytes(hashlib.sha256(f"{GLOBAL_SEED}:{case_id}".encode()).digest()[:8], 'big') % (2**32)

def load_adapted_shape(path, source_frame):
    return adapt_shape(cq.importers.importStep(str(path)).val(), source_frame)

def sample_shape(shape, n=SURFACE_SAMPLE_N, seed=0):
    verts, tris = shape.tessellate(0.05, 0.1)
    xyz = np.array([[v.x, v.y, v.z] for v in verts], dtype=float)
    tri = np.asarray(tris, dtype=int)
    if len(tri) == 0: raise ValueError('no triangulated faces')
    a, b, c = xyz[tri[:,0]], xyz[tri[:,1]], xyz[tri[:,2]]
    areas = np.linalg.norm(np.cross(b-a, c-a), axis=1) * 0.5
    good = areas > 1e-14
    if not good.any(): raise ValueError('zero-area surface')
    a, b, c, areas = a[good], b[good], c[good], areas[good]
    rng = np.random.default_rng(seed)
    idx = rng.choice(len(a), size=n, p=areas/areas.sum())
    u, v = rng.random(n), rng.random(n)
    flip = (u+v) > 1
    u[flip], v[flip] = 1-u[flip], 1-v[flip]
    pts = a[idx] + u[:,None]*(b[idx]-a[idx]) + v[:,None]*(c[idx]-a[idx])
    return pts, float(abs(shape.Volume()))

def geometry_metrics(pred_shape, gt_shape, n=SURFACE_SAMPLE_N, seed=0):
    p, vp = sample_shape(pred_shape, n, seed); g, vg = sample_shape(gt_shape, n, seed)
    d1 = cKDTree(g).query(p, k=1)[0]; d2 = cKDTree(p).query(g, k=1)[0]
    return {'chamfer': float(0.5*(d1.mean()+d2.mean())), 'h95': float(max(np.percentile(d1,95), np.percentile(d2,95))), 'gt_volume': vg, 'pred_volume': vp, 'absolute_volume_error': float(abs(vp-vg)), 'relative_volume_error': float(abs(vp-vg)/max(abs(vg),1e-12))}
