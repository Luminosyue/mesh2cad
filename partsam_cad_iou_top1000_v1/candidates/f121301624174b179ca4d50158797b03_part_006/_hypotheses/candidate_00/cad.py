#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.032486225, 0.117906735, 0.259907365], 'basis': [[0.0, 0.906711113581376, 0.4217522454095783], [-0.9937527325227692, 0.04706933922829343, -0.10119280561453586], [-0.1116042409746574, -0.419117446323382, 0.9010466467302555]], 'axis': [0.4217522454095783, -0.10119280561453586, 0.9010466467302555], 'zmin': -0.03793260169253436, 'zmax': 0.0269722352905409, 'profiles': [{'outer': [[-0.04130619360487185, 0.020927297769226486], [-0.03335831301954782, 0.030517236493611755], [-0.02324651655806555, 0.03765382581037654], [-0.011613042294511513, 0.041984838293244515], [0.0007739904036130423, 0.04311562169124332], [0.01300838835704794, 0.040985732997173584], [0.024297087197603366, 0.03583951136665866], [0.033847264299018215, 0.02786945863502143], [0.04101086209843889, 0.017744065808049686], [0.04530370551549129, 0.00609981827505051], [0.04641138246280691, -0.006279806118051304], [0.044334418045863695, -0.01855694883352803], [0.039104677982460985, -0.029837021083511613], [0.031156744361373112, -0.039426960960842194], [0.021044999819612272, -0.046563553315836136], [0.009411532145458335, -0.05089456977580977], [-0.002981858646274556, -0.05204922122761447], [-0.015216226787127482, -0.04997103461332131], [-0.026498633748638634, -0.0447492193258158], [-0.036048774448071384, -0.03677918105047552], [-0.043212438462056114, -0.026653781422237788], [-0.04750525206652655, -0.015009544368429925], [-0.0486192882234929, -0.0026538012874196097], [-0.04653593701640179, 0.009647231079941788]], 'holes': []}], 'simplify_tolerance': 1.903296858377156e-05, 'sketch_entity_count': 36}
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
