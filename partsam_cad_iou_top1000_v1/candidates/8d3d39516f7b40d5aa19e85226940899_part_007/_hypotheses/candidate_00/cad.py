#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.082298765, -0.20960042, -0.36924945000000003], 'basis': [[-0.0, 0.9995326920494657, 0.03056791658501044], [0.6227223985630272, -0.023917647787195007, 0.782077208753866], [0.7824428505187521, 0.01903532633489224, -0.622431395435203]], 'axis': [0.03056791658501044, 0.782077208753866, -0.622431395435203], 'zmin': -0.04736909203455939, 'zmax': 0.028871146447573517, 'profiles': [{'outer': [[-0.17636390943784258, 0.009799490047200585], [-0.1754944697011197, 0.014221841117540625], [-0.17470895229917618, 0.01591223672404151], [-0.16991647387379621, 0.020891510280506783], [-0.16867782906814935, 0.021648797244680117], [-0.1629828442369922, 0.023071367567673196], [-0.1536055699453487, 0.02425134703958273], [-0.1326102992622838, 0.027332973618762614], [-0.10923493509828539, 0.03147680442653118], [-0.0864414373606046, 0.034956195916305825], [-0.06577760802538296, 0.03657401435441143], [-0.030088553217190717, 0.036117710476548125], [0.020720299003354366, 0.03467729915466253], [0.08226973257254104, 0.03490256144396825], [0.14088053778038992, 0.0336122656101367], [0.15705980297621844, 0.030719932480510994], [0.1585590758240411, 0.02911346077995483], [0.15981759465207943, 0.02379325692731509], [0.16071835976085055, 0.015442706285748951], [0.1611073280027384, 0.005033481728891594], [0.1603090114212386, -0.01677187499410954], [0.1591509527309321, -0.02552080571251705], [0.15773066717177367, -0.031414380261735375], [0.15623137564227907, -0.03365684836223235], [0.13996635321129908, -0.03593284079642387], [0.08131750732773241, -0.034971011112246375], [0.019806100382611068, -0.03217351685502089], [-0.030954985299114387, -0.03133679107393218], [-0.06669181606775931, -0.029781923643994374], [-0.08727960157648339, -0.02628907254514058], [-0.10991132955022916, -0.021248987074673976], [-0.13321064509611644, -0.015718340756957563], [-0.15408215858765917, -0.011983533971956985], [-0.16350718856087884, -0.010690372831031442], [-0.16911641296247548, -0.009199012741430779], [-0.17035508906583632, -0.00814178879917824], [-0.1749760467936895, -0.003224325795610329], [-0.17571378200795634, -0.0013395402926273396], [-0.17625270720456407, 0.0014084085475975215], [-0.176449675933033, 0.003036621312496193], [-0.17660072260628143, 0.007618163792181534]], 'holes': []}], 'simplify_tolerance': 6.754161012180397e-05, 'sketch_entity_count': 41}
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
