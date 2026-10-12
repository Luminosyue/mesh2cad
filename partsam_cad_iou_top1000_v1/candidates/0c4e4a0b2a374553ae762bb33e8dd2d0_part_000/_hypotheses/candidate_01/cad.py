#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.037444535, 0.258093245, 0.006564540000000008], 'basis': [[0.0, 0.9998258400952438, 0.018662515313857538], [-0.4123020305437464, -0.017002432679941212, 0.910888551301677], [0.911047219198601, -0.0076945929589572245, 0.41223022406137616]], 'axis': [0.018662515313857538, 0.910888551301677, 0.41223022406137616], 'zmin': -0.1777617036464633, 'zmax': 0.22083137095016292, 'profiles': [{'outer': [[-0.2925303994272537, -0.012152735942923936], [-0.28691216917769957, -0.009304018225785686], [-0.04911014052317273, -0.0009643628503925686], [-0.04371283029420668, -0.005092919402544046], [-0.04167788300312182, -0.013762184707029026], [-0.044209040702864126, -0.021915646280479987], [-0.04981218545879485, -0.024764949950362162], [-0.06601611682620379, -0.025333217722472264], [-0.07179391517095562, -0.028321137230388527], [-0.2683726268826791, -0.03288867725870412], [-0.2691624908057981, -0.03245750964497556], [-0.2876141776714329, -0.033104605633538994], [-0.293026622204972, -0.028975463330932854], [-0.29506108890393146, -0.020291016613817825]], 'holes': []}, {'outer': [[0.14469790715816994, 0.0283443808512313], [0.15783327368414637, 0.03559399223522914], [0.17584658545558324, 0.035582485065435196], [0.1904153421542962, 0.024971565076679064], [0.19597572809449412, 0.00785233865904127], [0.1904153421542962, -0.009283208076105656], [0.17584658545558324, -0.019852718663027978], [0.16268746304537116, -0.027102308443891183], [0.14469790715816994, -0.027090822877231878], [0.13012913809039606, -0.016503679257026192], [0.12456875627321845, 0.0006393231891133938], [0.13012913809039606, 0.01775109389575853]], 'holes': []}], 'simplify_tolerance': 9.820736339968513e-05, 'sketch_entity_count': 26}
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
