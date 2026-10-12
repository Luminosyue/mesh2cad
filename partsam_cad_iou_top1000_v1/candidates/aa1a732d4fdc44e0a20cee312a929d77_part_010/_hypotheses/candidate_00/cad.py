#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.15847789, -0.10524183, 0.32082352000000003], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.033328370000000024, 'zmax': 0.033328369999999996, 'profiles': [{'outer': [[-0.07494052999999995, 0.03104077999999999], [-0.06744399999999995, 0.045063349999999995], [-0.057362829999999976, 0.05736280999999999], [-0.045063349999999947, 0.067444], [-0.031040789999999985, 0.07494052999999999], [-0.015829859999999973, 0.07956521], [4.950000000003563e-06, 0.08111997], [0.01582986000000003, 0.07956521], [0.03104079000000004, 0.07494052999999999], [0.04506335, 0.067444], [0.05736282000000004, 0.05736280999999999], [0.067444, 0.045063349999999995], [0.07494053000000003, 0.03104077999999999], [0.07956521000000003, 0.01582986], [0.08111998000000004, 4.949999999989685e-06], [0.07956521000000003, -0.01582987000000001], [0.07494053000000003, -0.031040780000000004], [0.067444, -0.045063350000000016], [0.05736282000000004, -0.05736281], [0.04506335, -0.06744400000000002], [0.03104079000000004, -0.07494054000000001], [0.01582986000000003, -0.07956522], [4.950000000003563e-06, -0.08111997], [-0.015829859999999973, -0.07956522], [-0.031040789999999985, -0.07494054000000001], [-0.045063349999999947, -0.06744400000000002], [-0.057362829999999976, -0.05736281], [-0.06744399999999995, -0.045063350000000016], [-0.07494052999999995, -0.031040780000000004], [-0.07956519999999995, -0.01582987000000001], [-0.08111997999999998, 4.949999999989685e-06], [-0.07956519999999995, 0.01582986]], 'holes': [[[-0.04834121999999996, 0.02001879999999999], [-0.0076401199999999725, 0.0031639899999999915], [-0.006877599999999984, 0.004590009999999992], [-0.005847689999999961, 0.005847689999999989], [-0.004590009999999978, 0.006877589999999989], [-0.00316398999999995, 0.00764012], [-0.020018789999999953, 0.04834122], [-0.029070109999999982, 0.04350858999999999], [-0.037002359999999956, 0.03700234999999999], [-0.04350858999999996, 0.029070089999999993]], [[-0.04350858999999996, -0.0290701], [-0.037002359999999956, -0.03700236], [-0.029070109999999982, -0.04350859], [-0.020018789999999953, -0.048341220000000004], [-0.00316398999999995, -0.007640130000000009], [-0.004590009999999978, -0.0068776000000000115], [-0.005847689999999961, -0.005847690000000003], [-0.006877599999999984, -0.00459002], [-0.0076401199999999725, -0.003164], [-0.04834121999999996, -0.020018810000000012]], [[0.0045900000000000385, 0.006877589999999989], [0.0058476900000000165, 0.005847689999999989], [0.006877600000000039, 0.004590009999999992], [0.007640120000000028, 0.0031639899999999915], [0.04834121000000002, 0.02001879999999999], [0.043508590000000014, 0.029070089999999993], [0.03700235000000002, 0.03700234999999999], [0.029070110000000038, 0.04350858999999999], [0.020018820000000048, 0.04834122], [0.0031639900000000054, 0.00764012]], [[0.006877600000000039, -0.00459002], [0.0058476900000000165, -0.005847690000000003], [0.0045900000000000385, -0.0068776000000000115], [0.0031639900000000054, -0.007640130000000009], [0.020018820000000048, -0.048341220000000004], [0.029070110000000038, -0.04350859], [0.03700235000000002, -0.03700236], [0.043508590000000014, -0.0290701], [0.04834121000000002, -0.020018810000000012], [0.007640120000000028, -0.003164]]]}], 'simplify_tolerance': 3.2447992e-05, 'sketch_entity_count': 72}
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
