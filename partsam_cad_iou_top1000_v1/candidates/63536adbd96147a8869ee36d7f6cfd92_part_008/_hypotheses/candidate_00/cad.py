#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05071336, 0.204127405, 0.042356495], 'basis': [[0.0, 1.0, 0.0], [-1.0, 0.0, 0.0], [0.0, -0.0, 1.0]], 'axis': [0.0, 0.0, 1.0], 'zmin': -0.056811795, 'zmax': 0.056811795000000005, 'profiles': [{'outer': [[-0.022945104999999993, -0.06714618], [-0.018477195000000002, -0.05498952], [-0.01584970499999999, -0.04114982], [-0.013234314999999996, -0.013325110000000001], [-0.01433622499999998, 0.017623520000000004], [-0.01611607499999998, 0.035810079999999994], [-0.019845484999999996, 0.05216828], [-0.02534257499999998, 0.06827223], [-0.030791214999999983, 0.07781352000000001], [-0.04107111499999999, 0.09070878], [-0.031045554999999975, 0.09710192999999999], [-0.012846884999999975, 0.09918454], [0.002881705000000012, 0.09070878], [0.008705795000000016, 0.07927862000000001], [0.010013465, 0.06869602], [0.021467805000000006, 0.06849018], [0.033684975000000006, 0.056999480000000005], [0.034968495000000016, 0.04059282], [0.030016185, 0.028956819999999994], [0.039920755, 0.022672650000000003], [0.045781135, 0.008445479999999998], [0.044703485000000015, -0.008675549999999997], [0.04048985500000002, -0.01839846], [0.04426765500000002, -0.02569972], [0.044582435000000004, -0.03748102], [0.042427185000000006, -0.04329298], [0.03682107500000001, -0.05208355], [0.029541225170727232, -0.055306690757699936], [0.032365265000000004, -0.05969961], [0.030318974999999998, -0.07259488], [0.028284735000000005, -0.07656638], [0.01586169500000001, -0.0839645], [0.004995193872771999, -0.08589634746266636], [0.003087585000000004, -0.0917501], [-0.003402345000000001, -0.0960364], [-0.010134574999999979, -0.09803426], [-0.01859825499999998, -0.09918454], [-0.02694081499999998, -0.09735621], [-0.035307584999999975, -0.09494667], [-0.045781135, -0.09055139000000001], [-0.034992754999999987, -0.0840977], [-0.02915662499999999, -0.07864898000000001]], 'holes': []}], 'simplify_tolerance': 3.9673816e-05, 'sketch_entity_count': 45}
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
