#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.13491846000000002, -0.331677915, -0.003773565000000003], 'basis': [[-0.08194503454478833, 0.06653372550323251, 0.9944135330354842], [0.0, 0.9977691801857562, -0.0667582434718289], [-0.996636850268669, -0.00547050656744841, -0.08176222993804692]], 'axis': [0.9944135330354842, -0.0667582434718289, -0.08176222993804692], 'zmin': -0.03545520035412771, 'zmax': 0.03494289384788922, 'profiles': [{'outer': [[-0.03345049550457924, -0.006977678493129343], [-0.04246856748762879, -0.018016529341025076], [-0.05653035498561315, -0.0179690591248372], [-0.06712961454389132, -0.007828267603234363], [-0.0606741304860048, 0.013585254456661333], [-0.054919362060655175, 0.022978442588683194], [-0.03159384606759803, 0.046329652942021134], [-0.005174347024874596, 0.05860631443941154], [-0.02077991395289365, 0.07270109008025558], [-0.017592529083318147, 0.07695189293624057], [0.019112131808760136, 0.07996930533110284], [0.052019538570758514, 0.07668526074830155], [0.048754136159179604, 0.07232684682396305], [0.03627822819263489, 0.05946344251834821], [0.055584961905212234, 0.0422292468053431], [0.06596182769577577, 0.007333263086617311], [0.06456071361673422, -0.022585217283174586], [0.06354002657626195, -0.04733011208457209], [0.06356753081350451, -0.04905559235765861], [0.06389698372349191, -0.051665583698333996], [0.06498440908200746, -0.06577005735077557], [0.0404636812026366, -0.07091975120743395], [0.03919580970883196, -0.06282566591114659], [0.0376004322826697, -0.04789811194021653], [0.03669191671399295, -0.041702727339009815], [0.03346005490543819, -0.06145382663965217], [0.0318533873002447, -0.07257860372008001], [0.030173095219985655, -0.08088353192540626], [0.0029820114960016045, -0.08103278288080491], [0.001894586956936392, -0.0669093323238935], [0.0030864585475353042, -0.05523319512303482], [0.0015167068830705525, -0.04193648444258283], [-0.00028599509569695816, -0.05258115819218585], [-0.002730976924987725, -0.06112264774489974], [-0.007391122824550387, -0.0700616504725044], [-0.03102879448969535, -0.06519527404115327], [-0.032116219848210906, -0.05107182281890452], [-0.027337282651463343, -0.039537127444634605], [-0.027125738673527723, -0.02440051317585825], [-0.029216682859101745, -0.008235797799829773]], 'holes': []}], 'simplify_tolerance': 3.220041764238155e-05, 'sketch_entity_count': 43}
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
