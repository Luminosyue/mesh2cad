#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00158553, 0.248339115, 0.046688485], 'basis': [[0.0, 1.0, 2.387628977876234e-10], [-0.26638595181269953, -2.3013554559743707e-10, 0.9638664454564452], [0.9638664454564452, -6.360308178471434e-11, 0.26638595181269953]], 'axis': [2.387628977876234e-10, 0.9638664454564452, 0.26638595181269953], 'zmin': -0.014695707963039012, 'zmax': 0.014696029673967157, 'profiles': [{'outer': [[-0.013153450674003466, -0.013152709996491537], [-0.01546621109722737, -0.010334179996491503], [-0.01718447740224602, -0.007118329996491736], [-0.018243903000981575, -0.003627830003508737], [-0.018600573798256394, 1.3300035085709347e-06], [-0.018243903000981575, 0.003627829996491263], [-0.01718447740224602, 0.007118330003508265], [-0.01546621109722737, 0.010334170003508497], [-0.013153450674003466, 0.013152710003508462], [-0.010334576885950946, 0.015467259996491168], [-0.007119292104656217, 0.017184509996491702], [-0.003628766417429601, 0.01824313000350813], [1.1766156354258144e-06, 0.018600450003508375], [0.0036280781249002987, 0.018243129996491275], [0.0071193054239538, 0.017184510003508312], [0.010334108885560158, 0.015467259996491305], [0.013153476295825027, 0.013152709996491551], [0.01546621744172001, 0.010334169996491517], [0.017184247471443058, 0.007118330003508659], [0.018243457958552825, 0.003627829996491221], [0.018600573798256394, 1.3299964914288806e-06], [0.018243457958552825, -0.003627830003508779], [0.017184247471443058, -0.007118329996491342], [0.01546621744172001, -0.010334180003508484], [0.013153476295825027, -0.013152710003508448], [0.010334108885560158, -0.015464600003508695], [0.0071193054239538, -0.01718451999649169], [0.0036280781249002987, -0.01824313000350873], [-1.150993813875976e-06, -0.01860045000350836], [-0.003628766417429601, -0.018243129996491875], [-0.007119292104656217, -0.0171845200035083], [-0.010334576885950946, -0.015464600003508832]], 'holes': []}], 'simplify_tolerance': 7.440229519302558e-06, 'sketch_entity_count': 35}
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
