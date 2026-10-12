#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.20446461500000002, -0.437179835, 0.007240775000000005], 'basis': [[-0.0, 0.9207042795461797, 0.39026097630348644], [0.12975659423877178, -0.38696166201870874, 0.9129205323462024], [0.9915458770281659, 0.05063893514943842, -0.11946745161497435]], 'axis': [0.39026097630348644, 0.9129205323462024, -0.11946745161497435], 'zmin': -0.02489836994727668, 'zmax': 0.0624059955008877, 'profiles': [{'outer': [[-0.07162292811591976, 0.07396901936545422], [-0.06318083050387109, 0.08082470870965737], [-0.054196467879894704, 0.08693117832966832], [-0.04420202957794206, 0.09178937683066321], [-0.032715436370788165, 0.09488145517074373], [-0.021557620128394787, 0.09567382931522744], [6.469111903306701e-05, 0.08318463657873716], [0.01581758188208257, 0.07163470957459066], [0.02923375575429815, 0.05823080151063418], [0.041187965224729145, 0.04586865003826889], [0.05809588767797499, 0.027372961213893043], [0.06391485562797078, 0.019507314071255635], [0.07835590072962699, -0.01122383505049423], [0.08097247527615836, -0.01583870877712005], [0.08276992667362675, -0.023866440108256604], [0.08631658724293614, -0.0340247467019615], [0.08608336569019397, -0.04940968429680792], [0.07984360036065108, -0.06068827202225556], [0.06975610480346482, -0.07135084011854627], [0.05741323096217952, -0.08125425653221131], [0.044388585249233434, -0.09022324520013926], [0.03126294524153123, -0.09683036259290329], [0.018677740886080447, -0.09956994644773015], [0.0038724790198568677, -0.09537167141187684], [-0.004888510279476533, -0.0890183919596337], [-0.012013066610932743, -0.08501750452892598], [-0.015667301287184802, -0.0812018464657924], [-0.04096526614822673, -0.05852546845042989], [-0.04682809177817498, -0.050698147894115364], [-0.0596819531954764, -0.029185923451440752], [-0.06809312892948818, -0.014191130021887346], [-0.07707726932639772, 0.0025131795216480563], [-0.08361234302450658, 0.020919422556671154], [-0.0893638677073303, 0.045228552476402235], [-0.08539400029034613, 0.05568451210890643], [-0.07914416233592587, 0.06579287663201773]], 'holes': []}], 'simplify_tolerance': 3.904875515259152e-05, 'sketch_entity_count': 36}
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
