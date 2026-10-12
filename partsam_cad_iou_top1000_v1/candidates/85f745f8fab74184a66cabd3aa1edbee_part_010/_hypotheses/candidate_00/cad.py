#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.109253235, -0.331677915, -0.003773565000000003], 'basis': [[0.08366996661770738, -0.0686197721924881, 0.9941280921241704], [0.0, 0.9976262479673121, 0.06886123268329601], [-0.9964935206443601, -0.005761617039865557, 0.08347135486437368]], 'axis': [0.9941280921241704, 0.06886123268329601, 0.08347135486437368], 'zmin': -0.03482243533800184, 'zmax': 0.035367646380264385, 'profiles': [{'outer': [[-0.0270995507065063, -0.024431844382742225], [-0.029210764289093534, -0.008245588969591279], [-0.033446046874383475, -0.006985715709291006], [-0.04247981751947265, -0.01800488415444625], [-0.05652754696773288, -0.0179762282190806], [-0.06716129544979092, -0.007796678710752401], [-0.06068415106420699, 0.013588735500955743], [-0.0549212487021391, 0.022971326697557068], [-0.031577660918220875, 0.04629987374441962], [-0.005159207053817128, 0.058591838694121906], [-0.020824437834655485, 0.07274289466777896], [-0.017571550340478907, 0.07691288284474364], [0.019148892901706616, 0.07991490847030912], [0.05203156426787485, 0.0766653854213113], [0.04869742410787694, 0.07239110299426736], [0.03623916474568006, 0.059493249898959384], [0.05559442397242289, 0.04221785425899029], [0.06599747905177004, 0.007296762310920327], [0.06460509056690102, -0.022628883866317537], [0.06357496812469711, -0.04735820017632669], [0.06360684548134513, -0.049557216470662115], [0.06386061734408165, -0.05160598133883865], [0.06496933894882854, -0.06573493598769631], [0.04044437305227084, -0.07088095990165715], [0.03920934649969794, -0.06282890628845973], [0.037539661465279706, -0.04733235171803053], [0.03673106243174101, -0.04186086932737162], [0.03349762840272986, -0.06148727231680509], [0.031875624889203646, -0.07259128950499957], [0.03015837085600728, -0.08085075238206824], [0.0029711975712305087, -0.08100794565790817], [0.0018624751297839424, -0.06686001547161648], [0.0030878960126149244, -0.05522699403452137], [0.001545732981858459, -0.04215404140254068], [-0.0002433641053018127, -0.05262537007236978], [-0.0027072375154998827, -0.061142866406557694], [-0.007403548818109749, -0.07003699776449554], [-0.031030056648191306, -0.0651883552802089], [-0.032138778252938205, -0.05104042578011486], [-0.027325584218841206, -0.039549268446518494]], 'holes': []}], 'simplify_tolerance': 3.2184570825643456e-05, 'sketch_entity_count': 40}
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
