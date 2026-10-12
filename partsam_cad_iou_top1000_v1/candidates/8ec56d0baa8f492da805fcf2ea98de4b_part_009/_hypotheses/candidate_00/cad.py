#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.16892384500000002, -0.028393554999999994, 0.011916689999999994], 'basis': [[-0.2951609161861448, 0.020378685606884557, 0.955230204049836], [0.0, 0.9997725122393083, -0.02132894209055711], [-0.9554475566749625, -0.006295470088730063, -0.29509377069027787]], 'axis': [0.955230204049836, -0.02132894209055711, -0.29509377069027787], 'zmin': -0.034536626758714974, 'zmax': 0.057778952395362695, 'profiles': [{'outer': [[-0.1327260022562122, 0.06821162523661493], [-0.09552370191556903, 0.0965996936209321], [-0.006743832008881036, 0.13353748343093433], [0.09548401420788823, 0.0965968309097204], [0.13267266935370411, 0.06821928655599248], [0.13470333254339378, 0.0679610190952466], [0.13466282624459783, 0.06669871241794999], [0.1104364171418633, -0.08746218680175848], [0.10123472267483839, -0.13482866161950582], [1.292645284779987e-05, -0.13491195393778377], [1.3624179832350463e-05, -0.133895076610007], [-5.8959251947184235e-05, -0.13491195299685876], [-0.10120327234782116, -0.13482562749928775], [-0.11047689842848979, -0.087540797286377], [-0.13470333254339378, 0.0667027495750448], [-0.13466283579907343, 0.06796505618938671]], 'holes': []}], 'simplify_tolerance': 5.388133301735751e-05, 'sketch_entity_count': 16}
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
