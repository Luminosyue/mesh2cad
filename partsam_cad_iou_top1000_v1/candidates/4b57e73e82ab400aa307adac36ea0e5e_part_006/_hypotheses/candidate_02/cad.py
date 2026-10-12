#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.11719827, 0.124440545, 0.045909075], 'basis': [[0.0, 0.9985481353029919, 0.053866701058424435], [-0.8930139328286909, -0.024241578504322427, 0.44937563534915087], [0.45002901659096844, -0.04810371456069101, 0.8917173974256808]], 'axis': [0.053866701058424435, 0.44937563534915087, 0.8917173974256808], 'zmin': -0.12965170437680826, 'zmax': 0.1371501204490745, 'profiles': [{'outer': [[-0.0720406839832161, -0.018048737358818553], [-0.07208672645190352, 0.048046969737741044], [-0.0717621796348633, 0.05002434269161923], [-0.0646960625010494, 0.05048260658968561], [-0.051688528695533725, 0.05106795151570592], [-0.0341530058971007, 0.053019770059446435], [-0.013523088518217197, 0.054829672095393904], [0.007548912534398451, 0.05578827626131035], [0.027057360257921798, 0.05620256098894917], [0.04346234873972562, 0.0561530738069128], [0.055213480775419634, 0.05449445166888153], [0.0611886918944134, 0.051707968201864775], [0.061187817948750695, -0.01743346942850411], [0.06025322275727947, -0.0380080469470751], [0.054495114023628534, -0.03908529937649982], [0.04218296081620713, -0.03997944763972121], [0.04213076581024803, -0.04163012471044699], [0.03728889112732412, -0.042022626070081955], [0.028339112923589607, -0.0430841577605398], [0.015910046552377367, -0.043497265494582875], [0.013110806863531523, -0.04350853727625549], [0.013111072294280974, -0.04687455186243946], [0.01301822414369535, -0.04690665219015326], [0.011161300155773815, -0.047244324603508706], [0.007652081053683642, -0.0478004321953461], [0.0029490240335728712, -0.047981185763642055], [-0.0025734770255210625, -0.0480792479127107], [-0.008422334559026213, -0.04807383271102669], [-0.013937827262932027, -0.04797912058890741], [-0.018653161680593718, -0.04779355706084209], [-0.02222891801463031, -0.04753138076437034], [-0.023957986494607907, -0.04723142096758117], [-0.023990325278813222, -0.04336907476425256], [-0.027236450947908674, -0.04328149799280158], [-0.039245397521745766, -0.0430874608091891], [-0.048436661597310235, -0.04228531358420751], [-0.053049013230812486, -0.04165608369299532], [-0.05306941393757465, -0.03997246493402624], [-0.06499590704715445, -0.039041481441423435], [-0.07182135083117404, -0.03798855272132825]], 'holes': []}], 'simplify_tolerance': 2.6655083669263387e-05, 'sketch_entity_count': 40}
OUT = Path(__file__).resolve().parent

def vec(v):
    return cq.Vector(float(v[0]), float(v[1]), float(v[2]))

def build():
    s = SPEC
    kind = s["kind"]
    B = s.get("basis")
    center = s.get("center")
    if kind == "extrusion":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = None
        height = s["zmax"] - s["zmin"]
        for profile in s["profiles"]:
            solid = cq.Workplane(plane).polyline(profile["outer"]).close().extrude(height)
            for hole in profile["holes"]:
                cutter = cq.Workplane(plane).polyline(hole).close().extrude(height)
                solid = solid.cut(cutter)
            result = solid if result is None else result.union(solid)
    elif kind == "multi_loft":
        def loft(track):
            wires = [cq.Wire.makePolygon([vec(p) for p in section], close=True) for section in track]
            return cq.Solid.makeLoft(wires, ruled=bool(s.get("ruled", True)))
        outer = [loft(track) for track in s["outer_tracks"]]
        # Keep disjoint solids as a legal STEP compound.  Global Boolean fusion
        # is unnecessary for training geometry and scales poorly with profiles.
        for track in s.get("hole_tracks", []):
            cutter = loft(track)
            cut_outer = []
            for solid in outer:
                try:
                    cut_outer.append(solid.cut(cutter))
                except Exception:
                    cut_outer.append(solid)
            outer = cut_outer
        result = outer[0] if len(outer) == 1 else cq.Compound.makeCompound(outer)
    elif kind == "box":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["mins"][0]*B[i][0] + s["mins"][1]*B[i][1] + s["mins"][2]*B[i][2] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        dx=s["maxs"][0]-s["mins"][0]; dy=s["maxs"][1]-s["mins"][1]; dz=s["maxs"][2]-s["mins"][2]
        result = cq.Workplane(plane).rect(dx,dy,centered=False).extrude(dz)
    elif kind == "cylinder":
        xdir = [B[i][0] for i in range(3)]
        axis = [B[i][2] for i in range(3)]
        origin = [center[i] + s["zmin"] * axis[i] for i in range(3)]
        plane = cq.Plane(origin=origin, xDir=xdir, normal=axis)
        result = cq.Workplane(plane).circle(s["radius"]).extrude(s["zmax"]-s["zmin"])
    else:
        raise ValueError(kind)
    cq.exporters.export(result, str(OUT / "reconstructed.step"))
    cq.exporters.export(result, str(OUT / "reconstructed.stl"), tolerance=0.001, angularTolerance=0.05)
    return result

if __name__ == "__main__":
    build()
