#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.15606303, -0.07285750999999999, -0.05582924], 'basis': [[0.0, 0.7572858336471571, 0.6530835828263718], [-0.9997477207241497, 0.014668886887314762, -0.017009369898813263], [-0.02246096406807797, -0.6529188233730268, 0.7570947861254328]], 'axis': [0.6530835828263718, -0.017009369898813263, 0.7570947861254328], 'zmin': -0.06796537475883538, 'zmax': 0.07194314770197278, 'profiles': [{'outer': [[-0.12927238657252116, -0.0032176161135526815], [-0.12760763646239484, 0.00038119384352887153], [-0.12554856616632035, 0.004452152255309042], [-0.1231314277965048, 0.00883822290074929], [-0.11782919157799124, 0.017874382798265177], [-0.11257183807994231, 0.02613678836085818], [-0.1098740342453113, 0.030007527471661362], [-0.10708263042172335, 0.03347094135966924], [-0.10448883199783142, 0.036139611885011635], [-0.10244579365338606, 0.03775596883821561], [-0.09735509367741481, 0.0414318187030269], [-0.09002725399329085, 0.04412980937691552], [-0.08071359290029542, 0.046372641655744805], [-0.07761381333682656, 0.046131396283398914], [0.008867400655764324, 0.032162633120580986], [0.03488539586773419, 0.03156750515843007], [0.04721636138819472, 0.038356624573266836], [0.10632793057700227, 0.06847724092875472], [0.11228742710471588, 0.06875048483123256], [0.12223027990727925, 0.06596887414180409], [0.13223980335993252, 0.060028301598800654], [0.13244190482136106, 0.05902454255644005], [0.13260314350007987, 0.055725130629625946], [0.13279928304410388, 0.04287771542433371], [0.1328123521334969, 0.03381840029555167], [0.13265227351641265, 0.01212839288366004], [0.13231077185269985, -0.011466464562505163], [0.13184029326884786, -0.033371360253248224], [0.13131210191165185, -0.050256263320274684], [0.13080690676329768, -0.059537957079618356], [0.13058724190385648, -0.06084123728620197], [0.12079027199902143, -0.06684505464871746], [0.11106611661761917, -0.07005777553166054], [0.1042047960537963, -0.07063939242933598], [0.013280489977519768, -0.06983822491245505], [-0.029098890335408405, -0.058103979424165404], [-0.06569270860445034, -0.04199607276794274], [-0.11863012718871306, -0.020712649597728183], [-0.12640694179195788, -0.01725920109024845], [-0.13093994448449603, -0.013959678685472123], [-0.1311243818044972, -0.013286593007470381], [-0.1316651835499996, -0.00993417983522799], [-0.1313053739581176, -0.008472044520307453], [-0.13052243140800077, -0.0062124774420971455]], 'holes': []}], 'simplify_tolerance': 5.289550713669931e-05, 'sketch_entity_count': 56}
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
