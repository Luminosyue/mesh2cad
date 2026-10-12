#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.009398245000000006, 0.194750415, -0.0025075349999999913], 'basis': [[0.0, -0.0, 1.0], [0.0, 1.0, 0.0], [-1.0, 0.0, 0.0]], 'axis': [1.0, 0.0, 0.0], 'zmin': -0.12328978500000001, 'zmax': 0.12328978500000001, 'profiles': [{'outer': [[-0.166961845, -0.025270075000000003], [-0.167002635, 0.0002344349999999773], [-0.166166765, 0.013893944999999991], [-0.160295215, 0.02704374499999998], [-0.148327865, 0.036238434999999986], [-0.138806985, 0.04257888499999998], [-0.135585795, 0.049143594999999984], [-0.135157655, 0.05892951499999999], [-0.134933405, 0.07175312499999997], [-0.13322086499999997, 0.085167985], [-0.128470625, 0.09723724499999997], [-0.11980601499999999, 0.10724742500000001], [-0.10769596499999999, 0.11511690499999999], [-0.09393453499999999, 0.12153892499999996], [-0.08015271499999999, 0.127063885], [-0.06794071499999998, 0.13126368499999996], [-0.05870526499999999, 0.133710155], [-0.052201704999999994, 0.13485182499999998], [-0.04679907499999999, 0.13532073499999997], [-0.038521814999999994, 0.13546342499999997], [1.0195000000008843e-05, 0.135524645], [0.03852182500000001, 0.13546342499999997], [0.04679906500000001, 0.13532073499999997], [0.05220170500000001, 0.13485182499999998], [0.05870525500000001, 0.133710155], [0.067940705, 0.13126368499999996], [0.080152705, 0.127063885], [0.09393453500000001, 0.12153892499999996], [0.107695965, 0.11511690499999999], [0.119806015, 0.10724742500000001], [0.128470635, 0.09723724499999997], [0.13322086500000002, 0.085167985], [0.134933415, 0.07175312499999997], [0.13515766499999998, 0.05892951499999999], [0.135585805, 0.049143594999999984], [0.138806985, 0.04257888499999998], [0.148327875, 0.036238434999999986], [0.160295205, 0.02704374499999998], [0.166166775, 0.013893944999999991], [0.167002635, 0.0002344349999999773], [0.167002635, -0.012589175000000008], [0.166961865, -0.025270075000000003], [0.166758005, -0.03805291500000002], [0.16606481500000003, -0.051202735], [0.163496025, -0.06516803500000001], [0.15503528500000002, -0.07793049500000002], [0.140356425, -0.08630968500000001], [0.12824635500000003, -0.09260936500000001], [0.12280294500000001, -0.09998956500000002], [0.11880704500000001, -0.109245405], [0.11146760500000001, -0.11811388500000002], [0.100397305, -0.123924265], [0.087125165, -0.127410495], [0.07409767500000002, -0.130488975], [0.06343511500000001, -0.13275197500000002], [0.04985716500000001, -0.13468876500000002], [0.04563698500000001, -0.13513729500000002], [0.04133527500000001, -0.135381935], [0.030040695000000006, -0.135483875], [-0.03004070499999999, -0.135483875], [-0.04133527499999999, -0.135381935], [-0.04563699499999999, -0.13513729500000002], [-0.05546368499999999, -0.133954825], [-0.06343510499999999, -0.13275197500000002], [-0.074097665, -0.130488975], [-0.08712516499999999, -0.127410495], [-0.10039730499999999, -0.123924265], [-0.11146761499999999, -0.11811388500000002], [-0.11880703499999999, -0.109245405], [-0.122802945, -0.09998956500000002], [-0.12824634499999998, -0.09260936500000001], [-0.140356415, -0.08630968500000001], [-0.15503528499999997, -0.07793049500000002], [-0.163496015, -0.06516803500000001], [-0.16606481499999998, -0.051202735], [-0.166757995, -0.03805291500000002]], 'holes': []}], 'simplify_tolerance': 6.6801054e-05, 'sketch_entity_count': 79}
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
