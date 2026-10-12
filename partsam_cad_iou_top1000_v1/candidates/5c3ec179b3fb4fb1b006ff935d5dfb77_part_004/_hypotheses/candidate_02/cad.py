#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-12.58575964, 4.738121035000001, 14.33311367], 'basis': [[0.0, 0.9987772998899167, -0.049435869817444605], [-0.1333833979448886, 0.048994136250962536, 0.9898527384241039], [0.9910645131133873, 0.006593924296611921, 0.1332203100495381]], 'axis': [-0.049435869817444605, 0.9898527384241039, 0.1332203100495381], 'zmin': -2.885476496551144, 'zmax': 2.8084924070340436, 'profiles': [{'outer': [[-5.487483413615206, -0.8404092929474343], [-5.9153707090040335, 0.6532749887325813], [-5.501673148165383, 1.9508920113558148], [-4.208591193815612, 2.65722448879878], [-2.6326675910097572, 2.874811730441237], [-1.405897752597203, 2.863697467700437], [-1.2459280188848119, 2.844546169505505], [0.30589950586082026, 2.691804729144407], [0.7417138733860523, 2.6454932219127993], [1.5425524016550998, 2.607574984625432], [2.8052076847782406, 2.4444170019286995], [3.4681658743097783, 2.280331647805893], [4.0061763424365235, 2.1186647668087706], [5.475918523062588, 1.2992592725812173], [5.678637363312436, 0.22698176810438772], [5.5441119907166145, -0.8229493271081005], [4.603123035479173, -1.5919083233566202], [4.252079484222164, -1.8597888720939], [2.740426840440871, -2.14729617364555], [1.5188819199932584, -2.2296423815415736], [0.3161028670561851, -2.291752620618433], [-1.0732473943015741, -2.623818392568932], [-2.3109693856948246, -2.756333674968164], [-2.59450320978613, -2.7204468981548118], [-3.838827344212037, -2.424144632824878], [-3.9998410775538886, -2.3663134455607238], [-4.7763344223398585, -1.7895819091100438]], 'holes': []}], 'simplify_tolerance': 0.002318801614463294, 'sketch_entity_count': 27}
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
