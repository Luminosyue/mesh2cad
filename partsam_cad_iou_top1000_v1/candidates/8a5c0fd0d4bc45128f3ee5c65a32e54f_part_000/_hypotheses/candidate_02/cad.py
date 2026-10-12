#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.003244205, -0.132938655, 0.07215178], 'basis': [[-0.26108962013653975, 9.148266652787112e-06, 0.9653145653999357], [0.0, 0.9999999999550935, -9.476979815989944e-06], [-0.9653145654432846, -2.4743410601984688e-06, -0.26108962012481507]], 'axis': [0.9653145653999357, -9.476979815989944e-06, -0.26108962012481507], 'zmin': -0.16719509791722845, 'zmax': 0.1671841389277842, 'profiles': [{'outer': [[-0.1659889929571056, -0.3576064685689807], [-0.16766320110252872, -0.35496267846138535], [-0.16840208369463275, -0.35290139859563], [-0.16895624830950165, -0.2732291587000004], [-0.16914093210550743, -0.038783078743996675], [-0.1686732210631196, 0.19776913112457126], [-0.16728195328576767, 0.28389403116748974], [-0.1652932502729312, 0.29308000142537294], [-0.16306487229084676, 0.298994981418003], [-0.1608797623184817, 0.30280384129991916], [-0.15893432731536464, 0.30562684144727964], [-0.15314127805169092, 0.31239316177856236], [-0.1464561634117289, 0.319249121756892], [-0.14404308936959684, 0.3213551917830944], [-0.14015220266796757, 0.32413336207808513], [-0.13829327654530932, 0.3258810320036519], [-0.1356954633991938, 0.3291073120635121], [-0.1350863313487272, 0.33031717186512516], [-0.13481510710192943, 0.33152702212036356], [-0.13504308525619532, 0.3348878319757703], [-0.13666232857691696, 0.34308800178408233], [-0.13596668764599157, 0.3450596618075029], [-0.13328237266166665, 0.3473897820891291], [-0.12910855967646512, 0.3492269822294295], [-0.12381472950925017, 0.34980955216111387], [-0.11587951087933844, 0.3498099534180099], [-0.11426056078097972, 0.35200527245509156], [-0.11309727115789367, 0.3649105723568558], [-0.1115364127054643, 0.36706145826846615], [0.11148156814986393, 0.3670613519981054], [0.1130541234172754, 0.3649105775000666], [0.11421740338721582, 0.35200527740296517], [0.11583635706906273, 0.349809953889011], [0.12381482342981048, 0.3498095578078076], [0.12905370546771908, 0.3492269880387191], [0.13328247362447643, 0.3473897878801258], [0.13592353286312384, 0.345059668051086], [0.13661917640494547, 0.34308800807459244], [0.13536937529050436, 0.33703866795076987], [0.13481520545384304, 0.33300581785034117], [0.135043198483047, 0.330317177994746], [0.1356406188435934, 0.32910731820646827], [0.13829337750811915, 0.3258810379675348], [0.14014060159400285, 0.32413336830328393], [0.14399992493358346, 0.3213551980775989], [0.14942354164412228, 0.3162916083422119], [0.15656459328632477, 0.30853948861003266], [0.15889117957474636, 0.3056268484149672], [0.16306497586455276, 0.29899498855550694], [0.16529336349978288, 0.293080008548693], [0.16728203233138994, 0.28389403880750996], [0.16867329045559623, 0.19776913885813885], [0.16914092688371501, -0.03878313125233716], [0.16895615882029458, -0.27322920127559125], [0.16839027286235983, -0.35290145096283027], [0.16765137096396449, -0.3549627310969392], [0.1669124839405072, -0.3563070212312386], [0.16296665615182102, -0.3613705612268356], [0.15939026613806212, -0.36477613115548924], [0.15749978630650088, -0.36580675160198883], [0.15378194189387298, -0.3668822014535056], [0.14719504521339377, -0.3670614016202022], [-0.14725012405538604, -0.36706140804779475], [-0.15383700586092722, -0.3668821482146658], [-0.15754318241800996, -0.3658066984761956], [-0.15940210592977203, -0.36477607840197873], [-0.16296677982225746, -0.36137050874073107]], 'holes': []}], 'simplify_tolerance': 0.00014682483525196212, 'sketch_entity_count': 76}
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
