#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.23341831000000002, -0.168637865, 0.38191107], 'basis': [[0.0, 0.9999996309293954, 0.0008591513680341563], [-0.989035263050947, 0.00012687908436919174, -0.14767949195281632], [-0.14767954645699585, -0.0008497309992842428, 0.9890348980271044]], 'axis': [0.0008591513680341563, -0.14767949195281632, 0.9890348980271044], 'zmin': -0.11346986517059574, 'zmax': 0.11346181948626183, 'profiles': [{'outer': [[-0.10784645139454681, -0.013771610264783019], [-0.11346017276232534, -0.013726915665034036], [-0.11346017276232534, 0.004394767646782876], [-0.10784645139454681, 0.004408201134079656], [-0.10784645139454681, 0.012207154933096435], [-0.019874370339293283, 0.012284487303774887], [-0.019874370339293283, 0.030203979201908423], [-0.04630242024135186, 0.030198817361578485], [-0.04630242024135186, 0.03372791605909142], [-0.019874370339293283, 0.03373895372976043], [-0.019874370339293283, 0.03385365135348819], [-0.01487147392608691, 0.043357416045604655], [-0.007867403123033745, 0.047935675833421974], [0.007865408284428166, 0.047933657538644724], [0.014869459306776054, 0.04335360070906627], [0.019872355719982453, 0.033848552416779386], [0.019872355719982453, 0.03373385477480735], [0.026734280867569123, 0.033732974484763666], [0.026734280867569123, 0.030203875787250724], [0.019872355719982453, 0.030198880246955346], [0.019872355719982453, 0.012284819381961649], [0.08764842663823812, 0.012249062299736456], [0.10784442688488334, 0.012179484824947266], [0.10784442688488334, 0.004410367415132781], [0.11345810524867495, 0.004365657223762227], [0.11345810524867495, -0.013756026088054684], [0.10784442688488334, -0.013769456863729665], [0.10784442688488334, -0.02155183272581038], [0.019872355719982453, -0.02162915419941175], [0.019872355719982453, -0.04793722739848225], [-0.019874370339293283, -0.04793212846177345], [-0.019874370339293283, -0.021629483108929815], [-0.08764847711958108, -0.0215937287922969], [-0.10784645139454681, -0.02152416261766121]], 'holes': []}], 'simplify_tolerance': 4.538365560220006e-05, 'sketch_entity_count': 34}
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
