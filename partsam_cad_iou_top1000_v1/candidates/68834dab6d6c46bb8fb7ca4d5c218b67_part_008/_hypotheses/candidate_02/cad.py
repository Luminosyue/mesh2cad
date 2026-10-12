#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.316963645, -0.26028737, -0.07366479000000001], 'basis': [[0.0032064395619636967, 0.1425052257578048, 0.9897888559571948], [0.0, 0.9897939441320756, -0.14250595832971213], [-0.9999948593594546, 0.00045693674260393897, 0.003173714460657172]], 'axis': [0.9897888559571948, -0.14250595832971213, 0.003173714460657172], 'zmin': -0.006474808294169923, 'zmax': 0.007878727368264699, 'profiles': [{'outer': [[-0.07593667447906752, -0.015325022738395772], [-0.07593919963093342, -0.015082214139950836], [-0.07543278390472531, -0.011900284147044408], [-0.07396577895863601, -0.009028069693397096], [-0.07168475042636745, -0.006750198364621152], [-0.06880944434218231, -0.005289204980356589], [-0.06562358736094849, -0.004785942644052909], [-0.06243831709402572, -0.005292116197453598], [-0.05956470273149632, -0.006755736488204552], [-0.05728501470888986, -0.009035691786659961], [-0.05582266471381735, -0.011909244777092955], [-0.05528344065046451, -0.015334460008299263], [-0.05579116057042561, -0.018523019647609988], [-0.05725947130934485, -0.021397669774776362], [-0.059544418126191975, -0.023679738908028113], [-0.06242496427963335, -0.02514466365505914], [-0.06561605126604601, -0.025647885434878167], [-0.06880655147401882, -0.025141747658403803], [-0.07168408572020372, -0.023674191819345825], [-0.07396768541798042, -0.021390035138599914], [-0.07543264960007168, -0.018514044683455824]], 'holes': []}, {'outer': [[0.05578507495833278, 0.011231430770511978], [0.05528101748823371, 0.014418035426763905], [0.05579065291573439, 0.017644359900225726], [0.057258987813387806, 0.020521679433796423], [0.05954439029486353, 0.02280580397828248], [0.06242327710731982, 0.024270947039424597], [0.06561491572925385, 0.02477464409303134], [0.06880609429538234, 0.024268030480737068], [0.07168370789067452, 0.022800257049528046], [0.07396711192248603, 0.02051404483874428], [0.07543290194147358, 0.01763538458879964], [0.07593697941146985, 0.01444367258665726], [0.07543010207844807, 0.011252412631344742], [0.07396178708449867, 0.008375088813478565], [0.07167637466720311, 0.00609100671542414], [0.06877264404219607, 0.004607672514617451], [0.06558619969021119, 0.0041041343526932415], [0.062400196800825154, 0.00461058433487096], [0.05952780333902079, 0.006075798939816201], [0.057248299190967605, 0.00835814489700778]], 'holes': []}], 'simplify_tolerance': 3.0375235808480652e-05, 'sketch_entity_count': 50}
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
