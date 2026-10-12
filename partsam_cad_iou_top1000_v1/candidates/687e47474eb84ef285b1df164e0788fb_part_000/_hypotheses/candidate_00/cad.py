#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [2.310000000000159e-06, 0.296483515, 0.26585236], 'basis': [[0.0, 0.9999999965793835, 8.271174648043015e-05], [-0.5629689324568109, -6.835944364161196e-05, 0.8264780556163759], [0.8264780584434402, -4.656414361772615e-05, 0.5629689305311102]], 'axis': [8.271174648043015e-05, 0.8264780556163759, 0.5629689305311102], 'zmin': -0.10766263259775569, 'zmax': 0.11246442932603501, 'profiles': [{'outer': [[-0.0105669284232318, 0.01225778980457613], [-0.007132446129262497, 0.015114087354775343], [-0.0029476478257921893, 0.016834644799236746], [0.0015867415381303957, 0.01740817504489354], [0.006126445417681433, 0.016800911246077195], [0.010304595278091265, 0.015057869805333858], [0.013723207837244634, 0.012201576664594043], [0.016322853544213232, 0.008501894776725472], [0.01812312097619411, 0.004058747829217302], [0.018750289587389578, -0.00023697034733477463], [0.01812312097619411, -0.004364022141971632], [0.016322853544213232, -0.008579785164844653], [0.013723207837244634, -0.012189583251973155], [0.010304595278091265, -0.015045930091692588], [0.006126445417681433, -0.016788948639024776], [0.0015867415381303957, -0.0173961848360541], [-0.0029476478257921893, -0.01683393508559595], [-0.007132446129262497, -0.015102172541866422], [-0.0105669284232318, -0.012257070111567937], [-0.013192250204397871, -0.008624786997924187], [-0.01503968347156894, -0.004409010902728706], [-0.015666458896987614, -0.0002257393723347154], [-0.01503968347156894, 0.004103719068152509], [-0.013192250204397871, 0.008558102943299738]], 'holes': []}], 'simplify_tolerance': 6.960871976189528e-06, 'sketch_entity_count': 24}
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
