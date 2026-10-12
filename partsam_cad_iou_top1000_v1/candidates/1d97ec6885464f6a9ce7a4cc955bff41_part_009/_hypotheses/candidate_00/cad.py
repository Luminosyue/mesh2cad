#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-1.114145695, 2.496029495, 0.76164004], 'basis': [[-0.0, 0.9848884880482867, 0.17318968245816557], [0.501139731819679, -0.14987252831774756, 0.852289384216034], [0.8653663785886879, 0.08679223102102046, -0.4935667527728074]], 'axis': [0.17318968245816557, 0.852289384216034, -0.4935667527728074], 'zmin': -0.5259155843639038, 'zmax': 0.527094025599811, 'profiles': [{'outer': [[-0.25931243995352493, -0.08774148101422938], [-0.27330969329821536, -0.0033298707852169613], [-0.2605349931649376, 0.08127595500813894], [-0.22223821839394467, 0.15779355993302674], [-0.16216855074578393, 0.21873316925168462], [-0.15848361648723971, 0.22184145595755295], [-0.08252094574881673, 0.2612377976677641], [0.0018990765121477732, 0.27523410622486544], [0.08651233843636588, 0.2624610370720395], [0.16303694327861307, 0.22416852479140076], [0.22398188364340882, 0.1641048933911373], [0.2633814186266402, 0.08814969887487566], [0.26201247412105816, 0.08507167359907536], [0.2759544045343758, 0.0008381622491716999], [0.2636945652097319, -0.08087417553207689], [0.26460387476099945, -0.0808675937273381], [0.26323506695852317, -0.08394570135701966], [0.2602034364382282, -0.0896597869725676], [0.2263071537987409, -0.15738546459861047], [0.16623726980898562, -0.21832485924208894], [0.1625524448446828, -0.22143323115807406], [0.08658979593361123, -0.26082957973878296], [0.0021699800439414735, -0.27482611692615544], [-0.08244348003678614, -0.26205301961522354], [-0.15896808939905732, -0.22376038054162362], [-0.21991278469675782, -0.1636967213487826]], 'holes': []}], 'simplify_tolerance': 0.00011001204463020418, 'sketch_entity_count': 29}
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
