#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.218750135, -0.41712303500000003, -0.025555035000000004], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.061605434999999986, 'zmax': 0.06160543500000004, 'profiles': [{'outer': [[-0.132933015, -0.0023725750000000156], [-0.13034226499999998, 0.0030270949999999797], [-0.127124275, 0.008672224999999978], [-0.11430686500000001, 0.024625805], [-0.10961622499999998, 0.02948008499999999], [-0.09758966499999999, 0.03703416500000001], [-0.07419105499999999, 0.04799716500000001], [-0.059491925, 0.054160454999999996], [-0.04304744499999999, 0.06059642500000001], [-0.016512645, 0.07117761499999997], [0.0014862850000000039, 0.07701365500000001], [0.019103425000000004, 0.080804335], [0.032520805, 0.08317692500000001], [0.045201875, 0.08325873499999997], [0.05529218500000001, 0.08154062499999998], [0.07023675500000001, 0.07843170499999996], [0.09129005500000001, 0.07071401499999996], [0.101380365, 0.06515072499999996], [0.110134405, 0.058905645000000006], [0.124560815, 0.043306544999999974], [0.13088771500000002, 0.026943874999999978], [0.134187515, 0.012435624999999978], [0.13541471500000002, 0.004908814999999983], [0.135960145, 0.0007090449999999915], [0.135523795, -0.014044625000000005], [0.130205945, -0.029398245000000017], [0.128078785, -0.03417071500000002], [0.12265184500000001, -0.04396103500000001], [0.11659765500000001, -0.051951465], [0.099389585, -0.06553249500000002], [0.077054545, -0.077149985], [0.063200805, -0.08143155500000002], [0.04831078500000001, -0.08312235500000001], [0.04002035500000001, -0.083258735], [0.015558185000000004, -0.082195135], [-0.001977154999999998, -0.08014981500000001], [-0.034266145, -0.07551370500000001], [-0.05466789647334331, -0.0760568196873835], [-0.07004585499999999, -0.07788631500000001], [-0.084035925, -0.07924988500000002], [-0.093308105, -0.07859537500000002], [-0.09889867499999999, -0.07649546500000001], [-0.10732544499999999, -0.07265026500000002], [-0.115370435, -0.06746874500000002], [-0.120061065, -0.06400531500000001], [-0.12565163499999998, -0.057187545000000006], [-0.129524155, -0.048024445], [-0.13035831403122383, -0.045770953294747035], [-0.131760385, -0.042952005000000015], [-0.133369365, -0.03790685500000002], [-0.135878305, -0.028007435000000025], [-0.135960145, -0.015271795000000005], [-0.135441995, -0.012026545], [-0.133614805, -0.004417925000000017]], 'holes': []}], 'simplify_tolerance': 5.4384058000000005e-05, 'sketch_entity_count': 54}
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
