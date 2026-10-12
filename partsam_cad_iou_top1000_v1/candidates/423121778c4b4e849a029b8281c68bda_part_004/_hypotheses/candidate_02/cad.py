#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [4.7500000022182576e-07, 123.67782973999999, 14.122112755], 'basis': [[0.0, 1.0, 5.16327336296999e-10], [-0.9290978997123246, -1.9095533791255968e-10, 0.36983387182645583], [0.36983387182645583, -4.797186437176008e-10, 0.9290978997123246]], 'axis': [5.16327336296999e-10, 0.36983387182645583, 0.9290978997123246], 'zmin': -4.528249012226906, 'zmax': 3.1069359442133866, 'profiles': [{'outer': [[-5.55223659495838, -11.989444254690163], [-4.416126876670253, -10.476532454803538], [-3.7666250031993402, -9.259302614865918], [-3.34062257375878, -7.992537014865928], [-3.090672478452773, -6.656383984785581], [-2.8306912949313867, -3.617199414714015], [-2.753344497751755, -1.9541020348051292], [-2.744869418330984, -4.74857247599793e-07], [-2.753351586768729, 1.9541001351948695], [-2.830684205914413, 3.617198465285987], [-3.090679567469747, 6.656383035214419], [-3.3406296627757666, 7.99253702513407], [-3.7666179141823664, 9.259300715134085], [-4.416126876670253, 10.476532465196463], [-5.55223659495838, 11.989442355309837], [-6.53280641543334, 12.985620975320238], [-6.775681258660926, 13.280466555248735], [-6.515744309412256, 13.543129445346827], [-4.75727829602092, 14.458742625523685], [-1.4419968117124522, 14.955759525699373], [1.2582628610767586, 14.434054855697422], [3.7222732129479366, 12.671559815624333], [5.555650725981541, 10.164149765541758], [6.217565325124803, 7.224854945475207], [6.105869843899983, 4.463460445451201], [5.342650399953285, 2.191771985466974], [4.867560956435714, -4.756567772583647e-07], [5.342650399953285, -2.1917729345330264], [6.105869843899983, -4.4634613945487995], [6.217565325124803, -7.224855894524793], [5.555650725981541, -10.164150714458241], [3.7222803019649104, -12.671560764375666], [1.258248683042811, -14.434055804302579], [-1.4419968117124522, -14.955759524300626], [-4.75727829602092, -14.458743574476314], [-6.515744309412256, -13.543131344653174], [-6.775681258660926, -13.280466554751266], [-6.53280641543334, -12.985621924679762]], 'holes': []}], 'simplify_tolerance': 0.00598230381, 'sketch_entity_count': 38}
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
