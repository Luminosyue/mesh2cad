#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.00013844500000000093, -0.418326035, -0.298979135], 'basis': [[0.01499596518741886, -0.3174470849054981, 0.9481574074556921], [0.0, 0.9482640357713736, 0.31748278451372286], [-0.999887554192019, -0.00476096078417259, 0.014220134468908832]], 'axis': [0.9481574074556921, 0.31748278451372286, 0.014220134468908832], 'zmin': -0.05561382806263091, 'zmax': 0.055613818253744673, 'profiles': [{'outer': [[-0.0625040670832021, -0.0328274041867476], [-0.06647343981542439, -0.026444423439111905], [-0.07194083496062188, -0.000348029620552815], [-0.06647346981205102, 0.025767620081894694], [-0.06324571129119864, 0.03222867554348483], [-0.04850454905950545, 0.05323616561821096], [-0.026427381823589627, 0.06732138144048047], [-0.00037078210849608516, 0.07236802120751863], [0.02565114150621807, 0.06756932468320735], [0.047728308742133886, 0.05369437800441541], [0.062469440977200454, 0.03282723931467564], [0.06643933301969712, 0.026400455438851934], [0.07194135427089629, 0.00033700798008142607], [0.06643939301295039, -0.025811587939325843], [0.06321111518182358, -0.03222884027272802], [0.04846995295013041, -0.053236358795375145], [0.02639278571421459, -0.06735438455328241], [0.000370832102873824, -0.07236802096947066], [-0.025685797608846383, -0.06760232808166694], [-0.0477629648447622, -0.05369454301931619]], 'holes': []}], 'simplify_tolerance': 2.894720843539786e-05, 'sketch_entity_count': 23}
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
