#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.025301815000000005, -0.227490635, -0.02724551], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.18302019, 'zmax': 0.18302019, 'profiles': [{'outer': [[-0.272509275, -0.16508925500000002], [-0.272509275, 0.165654775], [-0.269182565, 0.168083075], [-0.258237575, 0.164756415], [-0.247325925, 0.158868195], [-0.241670435, 0.149919155], [-0.233819365, 0.148688435], [-0.217651425, 0.151981715], [-0.190305715, 0.161895395], [-0.16113028499999998, 0.172740815], [-0.13940671500000001, 0.178995015], [-0.11974573499999999, 0.182321665], [-0.096891075, 0.184317705], [-0.07031047499999998, 0.184317705], [-0.039571465, 0.181523205], [-0.006902934999999999, 0.175468565], [0.025532694999999994, 0.165654775], [0.056504575, 0.155475015], [0.08464875500000002, 0.148222565], [0.10717072500000002, 0.14356529499999998], [0.12120953499999998, 0.141170145], [0.131222995, 0.140737415], [0.14163565500000003, 0.142034885], [0.15154930500000002, 0.144662975], [0.15999922500000002, 0.148189185], [0.169613475, 0.151848675], [0.183020205, 0.15497577499999998], [0.19453069499999998, 0.15930044499999998], [0.198356445, 0.166552905], [0.19938772500000002, 0.173106555], [0.20241504500000002, 0.175269005], [0.268883165, 0.175269005], [0.271611095, 0.156972045], [0.272509305, 0.113624695], [0.272509335, 0.09047043499999999], [0.272509305, -0.115720395], [0.271611095, -0.159367205], [0.268883165, -0.173905015], [0.20241504500000002, -0.173905015], [0.19938772500000002, -0.171809075], [0.198356445, -0.165454985], [0.19453069499999998, -0.158402325], [0.183020205, -0.154077655], [0.169613475, -0.150850655], [0.15999922500000002, -0.147091505], [0.15154930500000002, -0.143465405], [0.14163565500000003, -0.140770795], [0.131222995, -0.139439945], [0.12120953499999998, -0.13987243500000002], [0.10717072500000002, -0.142334345], [0.08464875500000002, -0.147124885], [0.056504575, -0.154576665], [0.025532694999999994, -0.16508925500000002], [-0.006902934999999999, -0.17520248500000002], [-0.039571465, -0.181423545], [-0.07031047499999998, -0.184317705], [-0.096891075, -0.184317705], [-0.11974573499999999, -0.182221775], [-0.13940671500000001, -0.178828595], [-0.16113028499999998, -0.172407985], [-0.190305715, -0.16119682500000002], [-0.217651425, -0.151017075], [-0.233819365, -0.14762365500000002], [-0.241670435, -0.148887995], [-0.247325925, -0.15806973500000002], [-0.258237575, -0.164157515], [-0.269182565, -0.167584065]], 'holes': []}], 'simplify_tolerance': 0.00010900373400000001, 'sketch_entity_count': 67}
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
