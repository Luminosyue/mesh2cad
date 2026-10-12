#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.117315665, 0.014920935000000003, -0.21233988999999998], 'basis': [[0.0, 0.9606614806687233, 0.27772201849939154], [-0.8193717651546675, -0.15920762264158586, 0.5507112159382074], [0.5732625144445818, -0.22755758052016367, 0.7871388931316283]], 'axis': [0.27772201849939154, 0.5507112159382074, 0.7871388931316283], 'zmin': -0.015092827719270238, 'zmax': 0.04921761896635681, 'profiles': [{'outer': [[-0.10541213394347479, -0.008845871764817947], [-0.03160803051269995, 0.010830769411587015], [-0.03186808148933204, 0.013499062456265738], [-0.03104753398611296, 0.017961349923806255], [0.05597345346541176, 0.04107923828411857], [0.058338616166943136, 0.04029515049006841], [0.06175059046052592, 0.03677628408883443], [0.06403734903482834, 0.03276268134307696], [0.1108200668623433, 0.04538047119022624], [0.11218088188445006, 0.04493363899488331], [0.114075473181979, 0.04154558295958165], [0.11613262764647699, 0.0360227669269255], [0.11783067292151397, 0.029610176594720095], [0.11880998531847087, 0.023781711074152157], [0.11882866719113924, 0.01989387945541464], [0.11788648127955278, 0.01880914214136557], [0.07113171044388988, 0.006150958469067714], [0.07115773104507538, 0.001515153425461924], [0.06994499078349993, -0.003254118335780527], [0.06827553354012039, -0.005131511109784726], [-0.01874543344199627, -0.028283996253356387], [-0.021682627478087028, -0.024836689846373106], [-0.02278161646115642, -0.022383337304026203], [-0.09655627844246553, -0.04205609966003074], [-0.10462457164257141, -0.04317260603248845], [-0.11230327906517801, -0.040359031244428654], [-0.11783791595387594, -0.03423646599171056], [-0.11997521878579542, -0.026214945262795122], [-0.11821407335786517, -0.018170059632218752], [-0.11295863043942828, -0.011880685545437813]], 'holes': []}], 'simplify_tolerance': 4.7760777195386935e-05, 'sketch_entity_count': 33}
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
