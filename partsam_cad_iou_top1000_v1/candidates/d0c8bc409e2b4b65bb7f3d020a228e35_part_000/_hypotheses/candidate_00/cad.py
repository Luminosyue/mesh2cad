#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05112561, 0.010510814999999979, -0.08855230999999998], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.289514735, 'zmax': 0.289514735, 'profiles': [{'outer': [[-0.24765079, 0.10257829], [-0.23642592, 0.12636980999999997], [-0.22287752000000005, 0.14891772999999997], [-0.20723470000000005, 0.17005842], [-0.18956287000000005, 0.18956286], [-0.17005845000000003, 0.20723466000000001], [-0.14891772000000003, 0.22287748000000002], [-0.12636982000000002, 0.23642591000000002], [-0.10257830000000003, 0.24765078000000001], [-0.07780506000000002, 0.25651941], [-0.05231182000000002, 0.26293359], [-0.026262270000000018, 0.26679525000000004], [-1.6380000000024153e-05, 0.26807151], [0.02626225999999998, 0.26679525000000004], [0.05231181999999998, 0.26293359], [0.07780502999999998, 0.25651941], [0.10257828999999999, 0.24765078000000001], [0.12636978, 0.23642591000000002], [0.1489177, 0.22287748000000002], [0.17005842, 0.20723466000000001], [0.18956286, 0.18956286], [0.20723466, 0.17005842], [0.22287748999999996, 0.14891772999999997], [0.23642586, 0.12636980999999997], [0.24765072999999999, 0.10257829], [0.25651938999999996, 0.07780505], [0.2629336, 0.05231181], [0.26679519999999995, 0.026262259999999996], [0.26807152, -1.6359999999999986e-05], [0.26679519999999995, -0.02626227], [0.2629336, -0.052311830000000004], [0.25651938999999996, -0.07780504], [0.24765072999999999, -0.10257830000000001], [0.23642586, -0.12636978], [0.22287748999999996, -0.14891771], [0.20723466, -0.17005841], [0.18956286, -0.18956285], [0.17005842, -0.20723467], [0.1489177, -0.2228775], [0.12636978, -0.23642586999999998], [0.10257828999999999, -0.24765074999999998], [0.07780502999999998, -0.25651939], [0.05231181999999998, -0.26293359], [0.02626225999999998, -0.2667952], [-1.6380000000024153e-05, -0.26807151], [-0.026262270000000018, -0.2667952], [-0.05231182000000002, -0.26293359], [-0.07780506000000002, -0.25651939], [-0.10257830000000003, -0.24765074999999998], [-0.12636982000000002, -0.23642586999999998], [-0.14891772000000003, -0.2228775], [-0.17005845000000003, -0.20723467], [-0.18956287000000005, -0.18956285], [-0.20723470000000005, -0.17005841], [-0.22287752000000005, -0.14891771], [-0.23642592, -0.12636978], [-0.24765079, -0.10257830000000001], [-0.25651939, -0.07780504], [-0.26293363000000003, -0.052311830000000004], [-0.26679523000000005, -0.02626227], [-0.26807152, 1.6369999999994722e-05], [-0.26679523000000005, 0.026262259999999996], [-0.26293363000000003, 0.05231181], [-0.25651939, 0.07780505]], 'holes': []}], 'simplify_tolerance': 0.00010722860800000001, 'sketch_entity_count': 112}
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
