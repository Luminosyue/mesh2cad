#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.212961755, 0.030340074999999994, -8.023499999999795e-05], 'basis': [[-0.017327715317262907, -0.13657587644021144, 0.990478056423499], [0.0, 0.9906267852948091, 0.13659638449268105], [-0.9998498638705133, 0.002366903263856563, -0.017165298921243775]], 'axis': [0.990478056423499, 0.13659638449268105, -0.017165298921243775], 'zmin': -0.051799386937438276, 'zmax': 0.051548201859320984, 'profiles': [{'outer': [[-0.07642296265185076, 0.00966670574738316], [-0.06266567686631062, 0.03339436073233241], [-0.05920494480305452, 0.06441003352783133], [-0.03705044750821152, 0.0760995181131554], [-0.012616457499416174, 0.09986905984169692], [0.015086380725628288, 0.13923314298030465], [0.03413852148834246, 0.09503682087687924], [0.05332696002643723, 0.0667066999818693], [0.07259543422683341, 0.050659818969049406], [0.06960126213141804, 0.019577026381114967], [0.07817173315172242, -0.006547781363249052], [0.0631479766537701, -0.03168738888687308], [0.0601302364416906, -0.05853721185318201], [0.03434373066547442, -0.07937835525325895], [0.010525173121409492, -0.10288482314736812], [-0.013013058763703584, -0.12998545459266395], [-0.030231342279694703, -0.09859517617074423], [-0.048635516687686245, -0.07066336470245871], [-0.06947069285465225, -0.04495730182089909], [-0.0668528626413362, -0.018040536689364922]], 'holes': []}], 'simplify_tolerance': 5.3843719514593725e-05, 'sketch_entity_count': 41}
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
