#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.072227705, 0.34468811499999996, -0.028462639999999997], 'basis': [[-0.0, 0.8889441387483765, 0.4580156309394989], [0.11265273308750799, -0.4551000960574455, 0.883285494218273], [0.993634420563174, 0.05159671262213393, -0.10014198679212555]], 'axis': [0.4580156309394989, 0.883285494218273, -0.10014198679212555], 'zmin': -0.08420521229019946, 'zmax': 0.1469467386888659, 'profiles': [{'outer': [[-0.16024687472953583, 0.06379943447616257], [-0.13793962077367017, 0.10873089347984434], [-0.10281531583916878, 0.14460125069874585], [-0.05828946541765888, 0.16786765014815616], [-0.008754490109660864, 0.17628127192844262], [0.040973249862242975, 0.16899208368622604], [0.08599411175574809, 0.14674677332427474], [0.12194225406244609, 0.111683001569304], [0.14526487235811833, 0.06726868706480038], [0.1536811060219893, 0.01783737455316945], [0.15369502867062843, 0.01649319478036462], [0.14640729269625685, -0.03322783214705314], [0.12409146562901553, -0.07825977925674903], [0.08896449502402508, -0.11421277457051814], [0.04446267969986756, -0.1375184982648603], [-0.0050846901559384846, -0.14595240117920943], [-0.0548000355800343, -0.13864291402404738], [-0.09984494568441621, -0.11635829886566292], [-0.1357676540068775, -0.08122020063868776], [-0.15910447426408567, -0.03671535356967647], [-0.16752285383722584, 0.0128389042622931], [-0.1675368074214249, 0.014183087038197503]], 'holes': []}], 'simplify_tolerance': 6.444673462153041e-05, 'sketch_entity_count': 22}
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
