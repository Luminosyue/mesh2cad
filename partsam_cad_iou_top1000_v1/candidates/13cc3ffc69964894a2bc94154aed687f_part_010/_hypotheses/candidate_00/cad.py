#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.21283099, 0.06508805000000001, 0.19388581], 'basis': [[0.0, 0.9376070017379713, -0.3476968655192796], [-0.9990223161942274, 0.015371236604628701, 0.041450414125380496], [0.04420872929547987, 0.3473569279245435, 0.9366903185561931]], 'axis': [-0.3476968655192796, 0.041450414125380496, 0.9366903185561931], 'zmin': -0.01737995999471141, 'zmax': 0.015418603640596641, 'profiles': [{'outer': [[-0.013270187696139251, 0.01098691328387582], [-0.0038790163954412434, 0.01249485722804719], [0.0036521802144015014, 0.012350272423011207], [0.004252299760953291, 0.015397329880270115], [0.003886387257575641, 0.028216192574112203], [0.0025016735273100184, 0.03391276579552646], [-0.0018465773835191217, 0.045397046144796976], [-0.001419079241895069, 0.04550585058608974], [-0.0005251319767068736, 0.045566370094393537], [0.00252154321432619, 0.045514424619245555], [0.004549417178471267, 0.0454228448345883], [0.009330395061640948, 0.04508124441334632], [0.01429604971372549, 0.04457812173404633], [0.01882101444830695, 0.04402424048762806], [0.02209895975004803, 0.04350883154992116], [0.023168556909478735, 0.043256823664793324], [0.02372193708203194, 0.04304544811895112], [0.023801939205612063, 0.04290145050983293], [0.018789292975989323, 0.03126805637043101], [0.01550958345604178, 0.027123812650069377], [0.012821861811394684, 0.014595347522285168], [0.01210467134522598, 0.007236854306781044], [0.013596445392181833, 0.006211450230321534], [0.01342560735716346, -0.032648694200376194], [0.010956310121538124, -0.04328854631972055], [0.0051561872902003225, -0.048678396830418066], [-0.0002720957476091424, -0.050818534693497876], [-0.007679903914438622, -0.04924910907211268], [-0.0129864247952833, -0.04449350352937395], [-0.020653028265437526, -0.028539981501780914], [-0.02329341314252824, -0.017526391335408165], [-0.023563651944272946, -0.0015580997755486727], [-0.01983902993562642, 0.006631149621175061]], 'holes': []}], 'simplify_tolerance': 1.9276980957578283e-05, 'sketch_entity_count': 33}
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
