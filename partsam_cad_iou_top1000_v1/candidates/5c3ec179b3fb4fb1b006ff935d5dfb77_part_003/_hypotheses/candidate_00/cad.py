#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-1.2686409950000002, 4.72080994, 14.33284378], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -2.6701202399999997, 'zmax': 2.67012024, 'profiles': [{'outer': [[-5.180870059999998, 0.9415259350000001], [-4.46473885, 1.894363405], [-3.685577389999999, 2.4768204650000003], [-2.4323902099999994, 2.788905625], [-1.0519981399999985, 2.663771155], [-0.9979887118276037, 2.642387405068024], [-0.28377982805054236, 2.4146885711475825], [0.1836719500000008, 2.285224915], [1.4067401900000007, 2.147418495], [2.6366233800000014, 2.126249315], [3.9923934899999995, 1.8836789150000002], [4.488307950000001, 1.6168155650000002], [5.36254883, 1.037906645], [5.61370468, -0.7376332249999997], [5.261791230000002, -1.3988907349999997], [3.9491577200000005, -2.1642010249999997], [3.3569831899999993, -2.299155955], [2.6905174300000017, -2.486568925], [1.41372681, -2.728141065], [0.12689224037825786, -2.7032176640525387], [-1.0726680799999997, -2.788905625], [-1.955881556283721, -2.7659246270376707], [-2.30211639, -2.762153145], [-3.8890380899999997, -2.5541682249999997], [-4.422557829999999, -2.270464185], [-5.1920661899999985, -1.8549864249999999], [-5.61370468, -0.5531144149999998]], 'holes': []}], 'simplify_tolerance': 0.002245481872, 'sketch_entity_count': 54}
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
