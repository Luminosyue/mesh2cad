#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.23476927000000003, -0.08198380999999999, -0.048340125], 'basis': [[0.0, 0.9921358939171038, -0.12516536262604608], [-0.0005199839293390089, 0.12516534570473387, 0.9921357597886127], [0.9999998648083475, 6.508397707543337e-05, 0.0005158947205572856]], 'axis': [-0.12516536262604608, 0.9921357597886127, 0.0005158947205572856], 'zmin': -0.04097779493687316, 'zmax': 0.041667480056583564, 'profiles': [{'outer': [[-0.03463663994567164, 0.027368253976277065], [-0.02316473149657811, 0.03875071413930898], [-0.013876208547004177, 0.04257928458194287], [-0.013876208547004177, 0.043646921484144466], [-0.011285597168210959, 0.04364709032533652], [-0.008176303522888726, 0.04492868803603563], [0.008080364279345192, 0.04492974608477323], [0.011201612256148253, 0.043648555912678653], [0.013852377693922243, 0.043648728674367275], [0.01385498841986262, 0.0425594148097975], [0.02312644224524077, 0.03875372695340689], [0.034598350678734784, 0.027372763820390254], [0.040824309837036964, 0.01244541299987992], [0.04083153404656502, -0.005422372336427579], [0.03460558488826149, -0.02029333694247861], [0.02313366643916931, -0.031732983819086714], [0.01388345276172936, -0.0355311658586876], [0.01388345276172936, -0.03652071149629569], [0.011473099431258602, -0.03652086848049988], [0.008087598473272374, -0.03791097138861277], [-0.008169079318560509, -0.03791203194130813], [-0.011541614312011568, -0.036522367408676114], [-0.013845133484396893, -0.03652251743486504], [-0.01386009448215726, -0.03556702975663735], [-0.023157507292249892, -0.03173599913649154], [-0.034629405741344765, -0.020297845534938345], [-0.040855364899646945, -0.005427691348712296], [-0.040862589103975167, 0.012440092735941745]], 'holes': []}], 'simplify_tolerance': 1.6568355605216275e-05, 'sketch_entity_count': 28}
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
