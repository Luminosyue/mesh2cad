#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.0031893100000000008, -0.094582215, 0.243704825], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.30894615, 'zmax': 0.30894615, 'profiles': [{'outer': [[-0.07122183740600284, 0.090271510041057], [-0.07103705499999996, 0.090573655], [-0.06817053792999536, 0.09125189047528165], [-0.052556484999999986, 0.096268675], [-0.03087008499999999, 0.092006835], [-0.025137364999999967, 0.085104915], [-0.013483285000000012, 0.072734255], [-0.002357214999999996, 0.061193315], [0.006355045000000004, 0.044900224999999995], [0.02076233500000002, 0.028644875], [0.02095483887889721, 0.028220725390815646], [0.02688856665645455, 0.03231615771863228], [0.007524235000000018, 0.063116805], [-1.8864999999979037e-05, 0.076053185], [-0.005487624999999996, 0.08578377499999999], [-0.008316274999999984, 0.091818255], [-0.008316274999999984, 0.094156615], [0.006694485, 0.097362425], [0.009447705, 0.095853815], [0.014614735000000018, 0.09064908499999999], [0.021742955000000008, 0.08223852499999999], [0.030342075000000024, 0.071414205], [0.03988407500000002, 0.058025215], [0.04972781500000001, 0.043429344999999994], [0.059232115, 0.028644875], [0.06779351500000003, 0.014690164999999991], [0.07477088500000001, 0.002621214999999996], [0.07974930500000002, -0.00680765500000001], [0.08235166500000002, -0.012992975000000004], [0.08238938500000001, -0.015444475], [0.07318682500000001, -0.026532824999999996], [0.07047130500000001, -0.024986494999999997], [0.06515343500000001, -0.019442315], [0.05753491500000002, -0.010126604999999997], [0.04806832500000002, 0.001112594999999994], [0.03837653707483059, 0.01491818103403762], [0.029705452276849783, 0.008940234659263873], [0.032076985, 0.0037149650000000006], [0.04256187500000003, -0.013521005000000003], [0.054593105, -0.034453065000000005], [0.06654889500000002, -0.05308449500000001], [0.071037025, -0.06368252499999999], [0.04738946500000002, -0.075638325], [0.014727875000000001, -0.090799925], [0.001074875000000003, -0.097362425], [-0.04467395499999999, -0.0021309250000000057], [-0.061645895000000006, 0.033019885], [-0.06276205859608391, 0.03549096280720021], [-0.07488402499999997, 0.061231034999999996], [-0.08238938499999998, 0.075185745], [-0.07345086499999998, 0.08955532499999999]], 'holes': []}], 'simplify_tolerance': 3.8944970000000005e-05, 'sketch_entity_count': 51}
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
