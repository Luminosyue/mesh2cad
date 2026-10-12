#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.05534724, -0.474151745, 0.05600899], 'basis': [[0.0, 0.9917253934666979, 0.12837734984538135], [-0.2130096160672629, -0.12543110286896822, 0.9689653976773122], [0.9770501028416492, -0.027345610002297373, 0.21124704530649654]], 'axis': [0.12837734984538135, 0.9689653976773122, 0.21124704530649654], 'zmin': -0.03402560403366824, 'zmax': 0.02128650740314943, 'profiles': [{'outer': [[-0.03820603541519641, -0.01027050291254683], [-0.03422676879754554, -0.006461439803562051], [-0.032443698118073315, -0.00565498532165494], [-0.02911590583786116, -0.0020819059772301533], [-0.022166469876730478, 0.0033659960725292096], [-0.013093149439361917, 0.009729679503405014], [-0.002192466573182091, 0.017159650453660445], [0.009559639179747741, 0.0246237256757248], [0.02106526559534598, 0.03074918842915087], [0.031234709113797283, 0.034214718699619756], [0.03908383791906266, 0.03405348618968442], [0.04397593169634298, 0.03069171400815604], [0.04536251676798714, 0.02490637809830371], [0.04271014243886587, 0.017519279768643654], [0.035841008141339975, 0.009246728128324316], [0.026009883113755298, 0.0006926402721730267], [0.01484809133395622, -0.0076238939338448206], [0.004007880932797679, -0.01515250873846003], [-0.005180480763892006, -0.021343095818178066], [-0.01275978114026034, -0.025872348672415585], [-0.01759472714778986, -0.027803741743929276], [-0.018777032197304724, -0.028935479413541545], [-0.023806832698027854, -0.03121035357877771], [-0.029113145860255922, -0.031431248425127054], [-0.03397425621461906, -0.029299871978529155], [-0.03782076843068835, -0.02534955555704585], [-0.04011694923023004, -0.020358286794179704], [-0.04034800013850181, -0.015092889633451819]], 'holes': []}], 'simplify_tolerance': 1.714210338129779e-05, 'sketch_entity_count': 40}
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
