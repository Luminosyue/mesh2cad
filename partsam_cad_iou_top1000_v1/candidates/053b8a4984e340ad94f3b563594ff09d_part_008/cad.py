#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.01888546, -0.052492205, -0.175816105], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.02712932500000001, 'zmax': 0.02712932500000001, 'profiles': [{'outer': [[-0.012984364999999998, -0.02818859], [-0.016162194999999997, -0.03583895], [-0.150631845, -0.03583894], [-0.15010218507389445, 2.500000069828368e-08], [-0.150631845, 0.035839], [-0.016162185000000003, 0.03583898], [-0.012984355000000003, 0.02818863], [-0.012902076855965281, 0.02255856], [0.01034323302708257, 0.02255856], [0.010260955000000002, 0.028188619999999998], [0.013379945000000004, 0.03583898], [0.123368465, 0.03583897], [0.12348618500000001, 0.05149277], [0.123545015, 0.04119421], [0.12344215356156016, 0.030238745753504787], [0.12364125653441978, 0.015097738386666218], [0.150397805, 0.014075190000000001], [0.150631845, 0.013490130000000003], [0.150163795, 0.008224599999999999], [0.150163795, -0.00944418], [0.12369531873817666, -0.010974469750396993], [0.12344186252445263, -0.03026039018731776], [0.123545005, -0.041194220000000004], [0.12348617499999999, -0.05149277], [0.123368465, -0.03583897], [0.013379934999999996, -0.03583895], [0.010260955000000002, -0.0281886], [0.01034336531354874, -0.02254948], [-0.012901952685958153, -0.02254948]], 'holes': []}], 'simplify_tolerance': 6.0252738e-05, 'sketch_entity_count': 32}
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
