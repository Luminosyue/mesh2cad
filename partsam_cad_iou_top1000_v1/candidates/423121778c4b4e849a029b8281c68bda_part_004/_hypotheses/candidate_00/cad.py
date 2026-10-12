#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [4.7500000022182576e-07, 123.67782973999999, 14.122112755], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -4.184325695, 'zmax': 4.184325695000002, 'profiles': [{'outer': [[-3.4035224900000003, -9.259302615000001], [-3.007732390000001, -7.992537015], [-2.7179527300000075, -6.656383985000001], [-2.5395698600000003, -5.2141652050000005], [-2.4251442000000054, -3.6171994150000004], [-2.418544770000011, -1.9541020350000002], [-2.448001860000005, -4.7500000022182576e-07], [-2.41855240000001, 1.9541001349999998], [-2.4251365700000065, 3.617198465], [-2.5395774900000134, 5.214164255], [-2.7179603600000064, 6.656383035], [-3.007740020000014, 7.992537025], [-3.4035148600000014, 9.259300715], [-3.9622917200000103, 10.476532465], [-4.936641699999996, 11.989442355], [-6.117107390000001, 13.280466555], [-5.80533982, 13.543129445], [-4.044872290000001, 14.458742625], [-0.838809970000014, 14.955759525], [1.6685981699999957, 14.434054855], [2.1669883699999986, 14.160242555], [4.246540069999995, 12.447136405], [5.138760159151715, 10.790960719692064], [5.54979324, 10.164149765], [6.117107389999987, 7.224854945], [5.99613570999999, 4.463460445], [5.298328399999988, 2.191771985], [4.411586759999992, -4.7500000022182576e-07], [5.298328399999988, -2.1917729350000004], [5.99613570999999, -4.463461395], [6.117107389999987, -7.224855895], [5.54979324, -10.164150715], [5.1387649847989465, -10.790957219406938], [4.246532439999996, -12.447136405], [2.1669883699999986, -14.160244465], [1.6685829099999978, -14.434055805], [-0.838809970000014, -14.955759525], [-4.044872290000001, -14.458743575], [-5.80533982, -13.543131345], [-6.117107390000001, -13.280466555], [-4.936641699999996, -11.989444255], [-3.9622917200000103, -10.476532455000001]], 'holes': []}], 'simplify_tolerance': 0.00598230381, 'sketch_entity_count': 42}
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
