#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.136702925, -0.044816554999999994, -0.005109625], 'basis': [[0.07938881652315197, 0.5691182405860955, 0.8184142252204812], [0.0, 0.8210055429507553, -0.5709202207350302], [-0.9968437268755084, 0.04532468065329075, 0.06517865841380828]], 'axis': [0.8184142252204812, -0.5709202207350302, 0.06517865841380828], 'zmin': -0.010011742462679466, 'zmax': 0.028828822708533455, 'profiles': [{'outer': [[0.0005282349892326264, -0.04735745475231952], [-0.00041929365012419786, -0.03664468533317125], [0.005305251000536008, -0.02641354120623391], [0.013970139907977153, -0.020209825727018245], [-0.015003987554133978, 0.13728577669382452], [-0.010455529186522795, 0.14855160766804296], [0.0014131813103378, 0.15512378803095153], [0.01608915326863886, 0.1544564981395143], [0.027957873733936725, 0.146805019739328], [0.0324708245279966, 0.13512718288550307], [0.04081486373711402, -0.035260103686901134], [0.040018350527224814, -0.04594328742978076], [0.034296606182561855, -0.056124872284094615], [0.024630760371840178, -0.060906258977305956], [-0.023133665997687545, -0.14589569481792383], [-0.04723617020775311, -0.13234697918585056]], 'holes': []}], 'simplify_tolerance': 6.020389656977507e-05, 'sketch_entity_count': 19}
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
