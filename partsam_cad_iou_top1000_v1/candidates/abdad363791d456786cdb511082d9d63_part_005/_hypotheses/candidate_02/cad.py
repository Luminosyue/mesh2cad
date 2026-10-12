#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [3.6652019000000005, 3.91202116, 2.0158913099999998], 'basis': [[0.0, 0.9999919998133762, -0.004000038655404551], [-0.4630000059468347, 0.0035454673689285275, 0.8863511855660638], [0.8863582765976922, 0.001852017921239876, 0.4629963018603803]], 'axis': [-0.004000038655404551, 0.8863511855660638, 0.4629963018603803], 'zmin': -0.8257780024162875, 'zmax': 0.7497120673962882, 'profiles': [{'outer': [[-3.1005729713079546, 0.43563112468924564], [-2.9512827246484314, 0.43747990757927535], [-2.3160502754155514, 0.43878013914332664], [-1.567690371799154, 0.43661316475752326], [-1.528805546729868, 0.43564201753163784], [-1.528805546729868, 0.38223245518835713], [-0.4737274038898089, 0.38223976574701407], [-0.4737274038898089, 0.5103026084101155], [-0.026778655024677248, 0.5129724861615701], [3.124832083256627, 0.5111272882026241], [3.124832083256627, -0.5098296438860397], [2.842765980306911, -0.5127299196094206], [-0.05443234728315537, -0.5132982265489231], [-0.4737274038898089, -0.5106543236785482], [-0.4737274038898089, -0.3996313860550755], [-1.528805546729868, -0.3996386961887621], [-1.528805546729868, -0.4979843232236437], [-1.6780960061153773, -0.49983310655815777], [-2.3133278355478977, -0.5011333346609677], [-2.7755195080962145, -0.5005361687739032], [-3.1005729713079546, -0.4979952160660359]], 'holes': []}], 'simplify_tolerance': 0.0012450810109129163, 'sketch_entity_count': 21}
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
