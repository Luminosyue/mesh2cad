#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.14942469, -0.411950885, 0.18690865], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.061246334999999985, 'zmax': 0.061246334999999985, 'profiles': [{'outer': [[-0.06894617000000001, 0.047609910000000005], [-0.06353862, 0.054428119999999997], [-0.05701430000000002, 0.05936543], [-0.049196870000000004, 0.062480640000000004], [-0.039910009999999996, 0.06265698], [-0.029506370000000004, 0.059071540000000006], [-0.019572950000000006, 0.05248844], [-0.01081509, 0.04437713], [-0.0030565963252186593, 0.036025997039354246], [0.005289999999999989, 0.029741500000000004], [0.01612177407345646, 0.028870595634562946], [0.024921709999999986, 0.02997661], [0.03532536, 0.030035389999999995], [0.04038024999999998, 0.02956517], [0.047492339999999994, 0.02515684], [0.050627189224548355, 0.022950832551448096], [0.05163982606375783, 0.02322451554090544], [0.05478074999999999, 0.025450730000000005], [0.05801354, 0.026685050000000002], [0.06253942999999998, 0.02644995], [0.06588972999999998, 0.023746180000000006], [0.06835837, 0.01992561000000001], [0.06976904, 0.015517300000000012], [0.07053316999999998, 0.010932639999999993], [0.07023932, 0.005995319999999998], [0.06700654, 0.0020572100000000038], [0.06418520999999999, 0.0015869900000000103], [0.059953199999999984, 0.0015869900000000103], [0.05839642819735098, 0.001809386540780922], [0.05777842999999999, -0.0013518899999999945], [0.05619142999999999, -0.007641100000000012], [0.05479159706125514, -0.012476891108235794], [0.056015099999999984, -0.01340131], [0.06001197999999999, -0.01598753], [0.06165773999999999, -0.01845619000000001], [0.06195162999999998, -0.02221796000000001], [0.06101118999999999, -0.02597974], [0.05985765243548274, -0.027710052479743258], [0.06077607999999998, -0.028036950000000005], [0.06818205999999999, -0.029859049999999998], [0.07282549999999999, -0.03238651000000001], [0.07323694999999997, -0.03414982], [0.07482392999999998, -0.03732381000000001], [0.07388354999999996, -0.04032147999999999], [0.07288426999999997, -0.04243748], [0.06882864999999999, -0.04396570999999999], [0.063063863934724, -0.04413544196023159], [0.06124631999999999, -0.04578781000000001], [0.05836621, -0.04872667], [0.054780759999999984, -0.05107777999999999], [0.049373219999999995, -0.052488460000000015], [0.04678906050745632, -0.05209968792565119], [0.046493110000000004, -0.05589756000000001], [0.043142810000000004, -0.05954179000000001], [0.03785280999999999, -0.06265698], [0.03068193999999999, -0.06195165999999999], [0.022511839999999977, -0.06007077999999999], [0.011873090000000003, -0.06230431], [-0.0018221200000000104, -0.056485339999999995], [-0.01304862000000001, -0.04320159000000001], [-0.023393480000000022, -0.030211729999999992], [-0.035560460000000016, -0.01957296], [-0.04896176000000002, -0.010756309999999991], [-0.06154019000000002, -0.0002351100000000106], [-0.07153238, 0.013812750000000013], [-0.07482393000000001, 0.027684269999999997], [-0.07329572000000001, 0.03896959]], 'holes': []}], 'simplify_tolerance': 2.9929572e-05, 'sketch_entity_count': 67}
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
