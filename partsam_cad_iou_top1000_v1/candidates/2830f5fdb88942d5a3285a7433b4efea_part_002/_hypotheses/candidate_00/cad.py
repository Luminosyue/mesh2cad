#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.006859254999999995, -0.008529340000000003, 0.12421512999999999], 'basis': [[0.0, 0.883057576855664, 0.4692646544944582], [-0.8733567006034384, 0.2285699804877725, -0.4301207243680494], [-0.48708117753725216, -0.4098354303590925, 0.7712242517655299]], 'axis': [0.4692646544944582, -0.4301207243680494, 0.7712242517655299], 'zmin': -0.0379073846070463, 'zmax': 0.037291357753896706, 'profiles': [{'outer': [[-0.0962781660173001, -0.09584875528049398], [-0.0949861611100526, -0.07739110971759273], [-0.0923472116191829, -0.05803023835758139], [-0.08820247847659954, -0.03854597800235046], [-0.08317145025909066, -0.019054003694121104], [-0.07716902932814586, 0.000595737915679256], [-0.06890864242433747, 0.019557733729337657], [-0.058683185943960894, 0.037485791467574504], [-0.04832420436776104, 0.05541449874770225], [-0.03628640533236206, 0.07220807127838484], [-0.008820669342007209, 0.10156049484347413], [0.005236409591281488, 0.11562525396255263], [0.02101597289369368, 0.12653733032364822], [0.03589754960263607, 0.13636010193273093], [0.05002079348902593, 0.14476962877411798], [0.06325021385101992, 0.1470606958974627], [0.07546568163545475, 0.14663727039154734], [0.07780201986848491, 0.14559367824281555], [0.08602205462448465, 0.14161344543358945], [0.08783068516465756, 0.1402349256576568], [0.09559938832207096, 0.13306378842913372], [0.09702104352108126, 0.1316056071507938], [0.10156047017840795, 0.12422556498821326], [0.10226301885473435, 0.12293484168874126], [0.10702605235014842, 0.11289207483132252], [0.10410108999750546, 0.0990397871813652], [0.09596825779879516, 0.09227903316952449], [0.09309130942649073, 0.08898577736755367], [0.08121906737544413, 0.07975892089268867], [0.043077986758768234, 0.04891500691444751], [0.031296706588303635, 0.038239517312042434], [0.02034883957280749, 0.027083186661690566], [0.010756277453502522, 0.015059392841566568], [0.0021170523824158693, 0.002535996125604312], [-0.008395214627220133, -0.020601893826478538], [-0.010419453561797715, -0.02558604506909734], [-0.015829024690259364, -0.040124372816497694], [-0.01956756663463039, -0.05524195390547607], [-0.0221477845911246, -0.07087822351531475], [-0.02235683882225493, -0.07563322910564535], [-0.022601181697287472, -0.08766798725500614], [-0.02381639662898191, -0.10507307833095543], [-0.025956004129855242, -0.11366301655486079], [-0.027811894888132994, -0.12213249395369483], [-0.03327353302894986, -0.1363424840296509], [-0.044104152637078856, -0.1446115768135964], [-0.05396656392162495, -0.14907612667702522], [-0.061830442858681056, -0.14853172703501902], [-0.0683570371435626, -0.14931093614268143], [-0.07740797747450648, -0.14567475466830984], [-0.0813249293594419, -0.14460342416454336], [-0.08727450533486167, -0.13830480106342521], [-0.09137577175340204, -0.13543512135384286], [-0.09651622927749243, -0.12607137630976722], [-0.09706582419426069, -0.11258167178205318]], 'holes': []}], 'simplify_tolerance': 5.9274326408028836e-05, 'sketch_entity_count': 67}
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
