#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.001205425000000003, 0.11711975999999999, 0.16336946000000002], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.036225469999999996, 'zmax': 0.03622547000000001, 'profiles': [{'outer': [[-0.029097410000000018, -0.103230975], [-0.017290380000000022, -0.095135525], [-0.008900820000000031, -0.09257243500000001], [-0.008060420000000013, -0.096045945], [-0.016407960000000027, -0.104071355], [-0.028215020000000035, -0.11185868500000001], [-0.036604600000000015, -0.114729905], [-0.03744498000000002, -0.11155052500000001]], 'holes': []}, {'outer': [[-0.036688670000000034, 0.11155052499999998], [-0.03583431000000001, 0.114729905], [-0.027458710000000025, 0.11185868499999999], [-0.01569369000000001, 0.10405735499999999], [-0.0073881600000000325, 0.09603193499999998], [-0.008242500000000014, 0.09255845499999998], [-0.016618100000000025, 0.09512152499999998], [-0.028383130000000034, 0.10323099499999999]], 'holes': []}, {'outer': [[-0.010889650000000028, -0.088748835], [-0.004390880000000014, -0.079742975], [0.005567369999999988, -0.071045265], [0.012960751904784035, -0.06814169387533703], [0.010525449999999992, -0.06355208500000001], [0.01432108999999998, -0.051352875000000006], [0.02156215999999997, -0.039251715000000006], [0.028257059999999973, -0.034741805], [0.030806129999999987, -0.039405795], [0.027010519999999982, -0.051745055000000005], [0.019769449999999966, -0.064000275], [0.013339254710824627, -0.06818394009833788], [0.014811339999999978, -0.071703565], [0.00831253999999998, -0.08089147499999999], [-0.0016596900000000192, -0.08977127500000001], [-0.00936298000000002, -0.092614485]], 'holes': []}, {'outer': [[-0.008494640000000026, 0.092432405], [-0.0008193400000000295, 0.089575195], [0.009068859999999984, 0.08066738500000001], [0.015483599999999986, 0.071451455], [0.01404729430187786, 0.06803537633314975], [0.020231619999999978, 0.06398627500000001], [0.027402699999999974, 0.051745055], [0.03111426999999997, 0.039391795], [0.02869316932681697, 0.035046914386556396], [0.03364935999999999, 0.030624054999999997], [0.037276879999999984, 0.017920644999999995], [0.03744497999999999, 0.005217234999999997], [0.03355129408823546, 0.000455199999999997], [0.03744497999999999, -0.004306845000000004], [0.037276899999999974, -0.017010265000000004], [0.03364933999999997, -0.029713675000000002], [0.02831302999999999, -0.034475705], [0.02441937999999999, -0.029713655000000002], [0.024587439999999988, -0.017010235000000002], [0.028215009999999985, -0.004306825000000003], [0.0335512743970691, 0.00045520000000468316], [0.028215009999999985, 0.005217224999999997], [0.024587439999999988, 0.017920634999999997], [0.02441937999999999, 0.030624054999999997], [0.028049052840993825, 0.03506319923921697], [0.02187026999999997, 0.039251715], [0.014699219999999985, 0.051338875], [0.011001659999999969, 0.063538085], [0.01337981511347599, 0.06797128889482285], [0.0062536599999999665, 0.07079316499999999], [-0.003634590000000021, 0.07951888499999998], [-0.010049310000000033, 0.088566755]], 'holes': []}], 'simplify_tolerance': 4.5891961999999996e-05, 'sketch_entity_count': 70}
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
