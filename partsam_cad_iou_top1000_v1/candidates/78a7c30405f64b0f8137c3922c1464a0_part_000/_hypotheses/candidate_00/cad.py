#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.14620342, -0.02731584, -1.5000000000431335e-07], 'basis': [[-0.0, 0.8841048471655253, 0.46728858237541315], [2.740911338026201e-07, -0.4672885823753956, 0.8841048471654921], [0.9999999999999625, 1.2807965735629604e-07, -2.42325299959991e-07]], 'axis': [0.46728858237541315, 0.8841048471654921, -2.42325299959991e-07], 'zmin': -0.0063068454523880135, 'zmax': 0.0063039060992764314, 'profiles': [{'outer': [[-0.28307738355436907, -0.06219482088939691], [-0.28307739644563434, 0.06219479043245909], [-0.2794143581505663, 0.07548928716837226], [-0.2693581094008718, 0.08522843613417011], [-0.2556387898555072, 0.08878380933999731], [0.25563877014452285, 0.08878379071230717], [0.2693580905991574, 0.0852284210208116], [0.2794142918494621, 0.07548927463100945], [0.2830773835543937, 0.062194778833424495], [0.28307739644564256, -0.06219480445111657], [0.2794143081505663, -0.07548929600942714], [0.2693581093914019, -0.08521229131364905], [0.2556387898460483, -0.08876768321101955], [-0.2556387701539653, -0.08876769262064435], [-0.26935809060860805, -0.0852123089104913], [-0.27941434184944564, -0.07548931150937926]], 'holes': []}], 'simplify_tolerance': 0.00011323095977928929, 'sketch_entity_count': 16}
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
