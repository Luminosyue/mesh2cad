#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.22072728, 0.0024881100000000017, -0.09984457000000001], 'basis': [[0.0, 0.7396729636276159, 0.6729664975898426], [-0.5702429934653442, -0.5528258715604237, 0.6076236369144482], [0.8214760668477709, -0.38375443008752025, 0.4217933249643944]], 'axis': [0.6729664975898426, 0.6076236369144482, 0.4217933249643944], 'zmin': -0.10243651179599939, 'zmax': 0.10873961871960716, 'profiles': [{'outer': [[-0.023996109163679814, 0.023272536727464065], [-0.027537340108287598, 0.03372533490785184], [-0.027507719862217006, 0.03497390119969231], [-0.02746395514650716, 0.035519635093102395], [-0.02548769659900954, 0.040453848957779176], [-0.02059283251423145, 0.038827448354058026], [-0.014597304243207706, 0.032857243553934753], [-0.009313501023673553, 0.024761633084896716], [-0.00434025311071461, 0.016397213240926006], [0.000729149271254777, 0.009622273792977153], [0.004916100406579782, 0.0038980317682243758], [0.007238689590959462, -0.0013462428401358204], [0.007960903261905246, -0.006953504667134114], [0.00732944551419266, -0.013771609087054628], [0.006510178870967364, -0.02194680122167295], [0.006649233307367286, -0.03164322539393363], [0.0064032879009056015, -0.04136911711310723], [0.004421953645811554, -0.04962840339134152], [0.0012584864830923, -0.053563877505593195], [0.0008980548559345916, -0.053325090972512694], [-0.0028743073534067613, -0.050080017160583704], [-0.003567409308469686, -0.04914149827185025], [-0.00418868199914509, -0.046836915056719275], [-0.005890402314971691, -0.03837926885796063], [-0.005968452846495075, -0.03484170171064794], [-0.005510104288301074, -0.030358515461966898], [-0.0044691552302069636, -0.025654362590730548], [-0.004486313787977906, -0.01839739395006771], [-0.007206389444373977, -0.00626317040850779], [-0.011235969177038426, 0.005766638906637777], [-0.015187937811161978, 0.012733309538688224], [-0.0188226349743807, 0.01687531190557072], [-0.021914147069652862, 0.020458084625338584]], 'holes': []}], 'simplify_tolerance': 1.8803545292674475e-05, 'sketch_entity_count': 42}
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
