#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.117315665, 0.014920935000000003, -0.21233988999999998], 'basis': [[-0.0, 0.9688886108342334, -0.24749719149054894], [0.5111886084747985, 0.2127160549093562, 0.832729299682315], [0.8594685605451773, -0.12651774491947446, -0.49528482073943236]], 'axis': [-0.24749719149054894, 0.832729299682315, -0.49528482073943236], 'zmin': -0.12149296937474421, 'zmax': 0.12268048405075242, 'profiles': [{'outer': [[-0.017057247305704917, 0.014321968814552487], [-0.01116276279372279, 0.01608506032374374], [-0.009765952847547742, 0.019177122874052488], [-0.0007712276986358975, 0.02614812647266477], [0.015098419060355231, 0.03098171943996903], [0.026283725273480628, 0.03286658646910979], [0.03709017086454986, 0.02927545382707591], [0.0450710652201359, 0.021003045780254973], [0.048390321316651025, 0.009970114497627277], [0.04628626045749156, -0.0013331775572079426], [0.03925730023091711, -0.010293030655620431], [0.028846203827070906, -0.014854646352656231], [0.01297650898276569, -0.01965335513124375], [0.0016532585738163698, -0.01882318862785818], [-0.0014267062145402972, -0.016878076060937667], [-0.007161333339375402, -0.018593352837324453], [-0.009400680032682436, -0.01622910080992451], [-0.01218226821917924, -0.010586171918228925], [-0.0148613851182644, -0.002983011041829806], [-0.016826770661833898, 0.00482960367133728], [-0.01760603878914645, 0.011078019102635523]], 'holes': []}], 'simplify_tolerance': 1.3199272021159495e-05, 'sketch_entity_count': 21}
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
