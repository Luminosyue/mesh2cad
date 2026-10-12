#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.04428899, -0.432739585, 0.206462095], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.01533, 'zmax': 0.015329999999999996, 'profiles': [{'outer': [[-0.04301174047467295, -0.051746826539153114], [-0.04215327499999999, -0.05177864500000001], [-0.03835022499999999, -0.05012950500000002], [-0.03757614499999998, -0.04911986500000004], [-0.035119314999999984, -0.031922015000000026], [-0.033604835, -0.027479505000000015], [-0.02869116499999999, -0.01899841499999999], [-0.025729484999999996, -0.01532998499999999], [-0.012502944999999988, -0.0033150050000000375], [-0.011796184999999987, -0.0021370950000000333], [-0.010853834999999978, 0.002742914999999957], [-0.011182053745301448, 0.003465054754370428], [-0.012200044999999993, 0.00405546499999998], [-0.012368324999999986, 0.004728585000000007], [-0.00859892499999998, 0.011257734999999991], [-0.007925814999999975, 0.011459614999999979], [-0.006906927483443006, 0.010856623392056891], [-0.006243054999999997, 0.01105579499999998], [-0.004392014999999999, 0.014219374999999979], [-0.004591493139429133, 0.01488437787470227], [-0.005603584999999994, 0.015464635000000004], [-0.005771884999999977, 0.01613774499999998], [-0.001531294999999988, 0.023508274999999967], [-0.0008581949999999783, 0.023676544999999993], [0.00015146500000001728, 0.023104395], [0.0008245649999999993, 0.023306274999999987], [0.0025746350000000195, 0.026335324999999965], [0.002408313776013221, 0.027000550594345946], [0.0013966950000000034, 0.027580524999999967], [0.0012284150000000105, 0.028253644999999994], [0.023743845000000013, 0.06726011500000001], [0.046292895, 0.054235544999999996], [0.023811125000000016, 0.015229014999999957], [0.023138025000000007, 0.015060815000000005], [0.02212836500000001, 0.01563289499999998], [0.021455255000000006, 0.015464635000000004], [0.01970517500000002, 0.01240196499999996], [0.019871500857826123, 0.011736750513004497], [0.020883135000000025, 0.011156764999999957], [0.021051385000000006, 0.01048365499999998], [0.01681084500000002, 0.0031131249999999944], [0.01613772500000002, 0.0029448549999999685], [0.015128075000000019, 0.003517004999999962], [0.014454975000000009, 0.003315065000000006], [0.012603915000000021, 0.00015148500000000675], [0.012803402218485214, -0.0005134921530073008], [0.013815505000000006, -0.001093775000000019], [0.013983784999999999, -0.0017668949999999906], [0.01021438500000002, -0.00829604500000003], [0.00954128500000001, -0.008497925000000017], [0.008493098382118175, -0.007896981006100473], [0.007723895000000008, -0.00799313500000004], [0.0039881449999999985, -0.011257675000000023], [0.003281375000000003, -0.012435585000000027], [-0.00045435499999998963, -0.02990272500000002], [-0.002170774999999986, -0.034311565000000044], [-0.007050784999999976, -0.04279270500000004], [-0.010147085, -0.04632648500000003], [-0.02381112499999999, -0.057062535000000025], [-0.024315955, -0.058240505], [-0.023811134999999983, -0.062380044999999995], [-0.02336594719025819, -0.06307969738449683], [-0.02233031499999999, -0.06369260500000001], [-0.02216204499999999, -0.06436577500000001], [-0.023710184999999995, -0.067058175], [-0.024383295, -0.06726011500000001], [-0.026066054999999977, -0.06631776500000003], [-0.04447548499999998, -0.05568262500000004], [-0.04612459499999999, -0.05470666500000004], [-0.046292895, -0.054033545000000016], [-0.04471107499999999, -0.05134108500000001], [-0.044071635, -0.051139145]], 'holes': []}], 'simplify_tolerance': 2.6904046000000004e-05, 'sketch_entity_count': 99}
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
