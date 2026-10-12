#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.070702475, -0.41888341500000004, 0.158981725], 'basis': [[0.0, 1.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]], 'axis': [0.0, 1.0, 0.0], 'zmin': -0.033056914999999965, 'zmax': 0.03305691500000002, 'profiles': [{'outer': [[-0.04806844499999999, 0.010812275000000003], [-0.046411964999999986, 0.015274175000000001], [-0.04423382499999999, 0.019284185000000002], [-0.041719914999999996, 0.022764445], [-0.03904946499999999, 0.025690565], [-0.03636147499999999, 0.028118455], [-0.03375297499999999, 0.030098815], [-0.031293345, 0.031709985], [-0.028692205, 0.033187425], [-0.02559165499999999, 0.034673035], [-0.021932485, 0.036105235], [-0.017651304999999978, 0.037406465], [-0.012739254999999977, 0.038451595], [-0.007249174999999997, 0.039107635], [-0.0013357349999999768, 0.039254145000000004], [0.004789365000000018, 0.038800945], [0.01083505500000001, 0.037752945], [0.01653565500000001, 0.036173925], [0.021701765000000012, 0.034203505], [0.026212645000000007, 0.031996105000000004], [0.030049305, 0.029693595000000003], [0.03325080500000002, 0.027415165], [0.035897415000000016, 0.025220685], [0.038061605, 0.023155465], [0.04005602500000002, 0.020994915000000003], [0.04210512500000002, 0.018440065], [0.04412260500000001, 0.015431785000000003], [0.04600198500000002, 0.011944475000000003], [0.047594895, 0.007957654999999994], [0.048733335000000017, 0.003538575000000002], [0.049255985, -0.0011921149999999936], [0.049039845, -0.006048714999999996], [0.048068445000000015, -0.010819915], [0.046411965, -0.015281815000000004], [0.044233825000000004, -0.019291825], [0.041720855, -0.022764444999999994], [0.039049465000000005, -0.025698205000000002], [0.036361475000000004, -0.028126095000000004], [0.03375297500000002, -0.030106455000000004], [0.031293345, -0.031717625], [0.028693125000000014, -0.03318742499999999], [0.025592594999999996, -0.034673035000000005], [0.021932485, -0.036112875], [0.017651305000000006, -0.037414105], [0.01273924500000001, -0.038459234999999994], [0.007249174999999997, -0.039115285], [0.0013366750000000094, -0.039254145000000004], [-0.004783394999999996, -0.038809315], [-0.010834114999999978, -0.037752944999999996], [-0.016535654999999982, -0.036181555000000004], [-0.021701764999999984, -0.034211145], [-0.02621264499999998, -0.032003745], [-0.030049324999999988, -0.029701234999999993], [-0.03324986499999999, -0.027415165000000005], [-0.03589648499999999, -0.025220684999999993], [-0.03806161499999999, -0.023163094999999995], [-0.040056024999999995, -0.021002544999999997], [-0.04210512499999999, -0.018447704999999995], [-0.044122604999999995, -0.015439424999999993], [-0.04600104499999999, -0.011944474999999996], [-0.04759488499999999, -0.007965294999999997], [-0.048733344999999983, -0.0035462150000000053], [-0.04925598499999999, 0.0011844750000000043], [-0.049038904999999994, 0.006048714999999996]], 'holes': []}], 'simplify_tolerance': 1.9702394e-05, 'sketch_entity_count': 64}
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
