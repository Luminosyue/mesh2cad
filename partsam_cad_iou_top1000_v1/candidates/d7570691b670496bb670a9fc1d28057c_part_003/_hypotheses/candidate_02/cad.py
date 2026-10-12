#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.20446461500000002, -0.437179835, 0.007240775000000005], 'basis': [[0.0, 0.8354263742292022, 0.5496023773986509], [-0.9883980274026768, 0.0834768749057756, -0.12688952195694775], [-0.15188594216219362, -0.5432259056766481, 0.825733780328314]], 'axis': [0.5496023773986509, -0.12688952195694775, 0.825733780328314], 'zmin': -0.06783322048996572, 'zmax': 0.06294957476945152, 'profiles': [{'outer': [[-0.06343520354626472, -0.02107312443441825], [-0.060168938978115157, -0.02121569543075837], [-0.06109205995901511, -0.012452197266362803], [-0.05628224597441882, 0.012598408552157945], [-0.049913399721465, 0.03911760794726931], [-0.04620266302516514, 0.04511712865046896], [-0.03282531927147402, 0.06366065063492542], [-0.026886478268247953, 0.0755987966163242], [-0.022207471916433984, 0.08392227655789286], [-0.018367362447279715, 0.09014256397776951], [-0.004113703196459852, 0.1038948506969419], [0.014034217546859882, 0.10090951209378507], [0.057508508198318965, 0.08022397735455589], [0.06057639804905771, 0.08067412712278532], [0.06220574981316897, 0.08284950842786162], [0.06299229450141791, 0.0827130018203444], [0.06890090718844569, 0.07762530933478883], [0.06836657909551534, 0.07610188672818664], [0.0659669822902662, 0.07198571309926037], [-0.02477344677806874, -0.07475928124867179], [-0.031433207073642, -0.08551864601788398], [-0.03445112240062558, -0.09016975879774955], [-0.03576594245951059, -0.09163356055376314], [-0.04350891858488038, -0.08950253183817207], [-0.04398872547055594, -0.08888605679997917], [-0.04360569551580037, -0.08640801966641118], [-0.05412784537388277, -0.07761168577089568], [-0.05721597194009624, -0.06625260039508706], [-0.06180842692609425, -0.04639191809729036], [-0.06392362194734881, -0.02118535267315911]], 'holes': []}], 'simplify_tolerance': 3.9105682250141004e-05, 'sketch_entity_count': 42}
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
