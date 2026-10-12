#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.35181253999999995, 3.8187114, 0.030253019999999964], 'basis': [[0.0, 0.9999432973139086, 0.010649044886197855], [-0.5873889848162062, -0.008618322623468951, 0.8092588615713421], [0.8093047513246088, -0.006255131664965969, 0.5873556782829865]], 'axis': [0.010649044886197855, 0.8092588615713421, 0.5873556782829865], 'zmin': -0.6233535872584088, 'zmax': 0.61250747831674, 'profiles': [{'outer': [[-0.6273542205676519, -0.6770344512746747], [-0.6287955403951309, -0.6450540034569768], [-0.6334475076718135, -0.6260473804037314], [-0.6274435368079612, -0.5784920142034172], [-0.6282665983311424, -0.5289850279454207], [-0.6243762294843835, -0.2436005165981409], [-0.6042257019653214, -0.23055492454512136], [-0.603503997407352, 0.26373228391502695], [-0.6173830376512762, 0.26937014081028593], [-0.6134923868578047, 0.5547550962694113], [-0.6115006655116604, 0.6007871211627498], [-0.617442445218318, 0.6553363402901671], [-0.6103168233602975, 0.6694661830750852], [-0.6081636780190165, 0.702113080601308], [-0.6094246867138279, 0.7348319136980836], [-0.6161623326863286, 0.7492525145805126], [-0.6087242722774768, 0.8037509938366382], [-0.6094648398416688, 0.8501713643882333], [-0.6082156262667096, 0.9418052390013145], [-0.5272082236954878, 0.9415177855234264], [-0.14365597382361597, 0.9371800187854875], [0.02860604219192892, 0.9389263734257007], [0.17569200236148222, 0.9427309324144066], [0.21152737514832223, 0.9420888470045671], [0.2962935158930298, 0.9376712258075578], [0.6275291716145117, 0.9243432097806157], [0.6305659330822468, 0.9173315976163522], [0.602201565965403, -0.9334965878878455], [0.1342636599637833, -0.9463694651017611], [0.05954223723677984, -0.9436529682690663], [-0.046305950405753124, -0.9385753579900014], [-0.14175675930930595, -0.9304718483074323], [-0.2029297087503241, -0.9243362161642357], [-0.5498013383972084, -0.9183920220220946], [-0.6335433589222376, -0.916034380722119], [-0.6322938634005653, -0.8244003319818825], [-0.6301362167295085, -0.7752894327734983], [-0.6348332685591866, -0.7277363828382014], [-0.6296662421591498, -0.7089362014926931]], 'holes': []}], 'simplify_tolerance': 0.00037782007950323354, 'sketch_entity_count': 42}
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
