#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.11733201, 0.014920935000000003, -0.21233988999999998], 'basis': [[0.0, 0.9606704370094094, -0.27769103596650474], [-0.8193771454040737, 0.15918772603417689, 0.5507089625832681], [0.5732548243054493, 0.22753368835453464, 0.7871514003508537]], 'axis': [-0.27769103596650474, 0.5507089625832681, 0.7871514003508537], 'zmin': -0.015082917884098839, 'zmax': 0.0492177510761025, 'profiles': [{'outer': [[-0.11821403592756807, 0.018135465871324145], [-0.11997520899878214, 0.0262148975631033], [-0.11783792717739393, 0.03420184896377183], [-0.112303299711526, 0.04032448083757367], [-0.10462458804478625, 0.043172681974307486], [-0.0965562781475582, 0.042056245947792836], [-0.02277769603113151, 0.022381381857211273], [-0.021682807165295675, 0.024836207731306], [-0.018745717942750893, 0.02828320783231237], [0.06827545886470555, 0.0051314745914218755], [0.06994481946182787, 0.003253713352346092], [0.07115759118754032, -0.0015154679508496223], [0.07113152803144933, -0.006150976865694755], [0.11788654724563341, -0.018808788689781288], [0.11882867749953113, -0.019893723143725447], [0.11880995757319719, -0.023816292099196414], [0.11783063297369058, -0.029610283631442167], [0.11613260458467876, -0.03602287777281579], [0.11407549185927278, -0.04158017588404197], [0.11218095779893549, -0.04493349878312354], [0.11082020228246306, -0.04541469076005959], [0.06405368227928673, -0.032768943271217744], [0.061750542617975274, -0.036811216478010673], [0.058338558701083475, -0.04033013978837649], [0.05597349962175223, -0.04111388000413492], [-0.03104769765467396, -0.01796216933851048], [-0.03186816107827163, -0.013499570472125126], [-0.03160713414116614, -0.010831936230766887], [-0.1054120466716802, 0.008846006074142536], [-0.1129585650968265, 0.011880759644826997]], 'holes': []}], 'simplify_tolerance': 4.7760777299662654e-05, 'sketch_entity_count': 33}
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
