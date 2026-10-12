#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.17924537499999998, -0.25381079, -0.14339902999999998], 'basis': [[0.42178183563247273, -0.25205253563747454, 0.8709590130478135], [0.0, 0.9605840513062945, 0.2779897127161113], [-0.9066973492464294, -0.11725101131634516, 0.40515690443924635]], 'axis': [0.8709590130478135, 0.2779897127161113, 0.40515690443924635], 'zmin': -0.07353934116293166, 'zmax': 0.05725012616194995, 'profiles': [{'outer': [[-0.06403603583804089, 0.02582366068018428], [-0.06743546284896838, 0.034753909638197175], [-0.0697442664159872, 0.041692109533862806], [-0.0711772983697419, 0.06144917445847562], [-0.05725547417541021, 0.07345614034451575], [-0.013513401492550463, 0.09357638159157887], [-0.011888665200167296, 0.09621305836111776], [-0.012509448764614961, 0.09887541418668172], [-0.011901319737451187, 0.09937296400533682], [-0.00421275112417458, 0.10065562663853825], [-0.0033735026116605443, 0.09927363233126744], [-0.001764385390105112, 0.09479822038740844], [0.02439739389335902, 0.016226307971654908], [0.05672973244460324, -0.08091190421331965], [0.05836695811516184, -0.08621387182629212], [0.05864571264626353, -0.08816712129083353], [0.052049190533134976, -0.0927315406929813], [0.05126868360601945, -0.09271836306562525], [0.04960432967572976, -0.09082945268964626], [0.03610521735431612, -0.0932679701772901], [0.0254122388156924, -0.08836487332602642], [0.007229705626187082, -0.07915716948987736], [-0.013483201820203126, -0.06462652166185266], [-0.013254741929018097, -0.06418629229558606], [-0.011048584186287616, -0.06176677466638475], [-0.018367933615286536, -0.05685941768418802], [-0.03451081132773902, -0.03711428113073142], [-0.0507973550462182, -0.015229889317383212], [-0.05302205101151378, -0.008540066727873847], [-0.05868845689527614, 0.013620046068896458]], 'holes': []}], 'simplify_tolerance': 3.8784719363165674e-05, 'sketch_entity_count': 30}
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
