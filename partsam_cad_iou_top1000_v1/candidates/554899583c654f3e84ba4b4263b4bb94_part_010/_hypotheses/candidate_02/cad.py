#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.07296532, -0.197613645, 0.042042235], 'basis': [[0.3979677397297961, -0.04583788164628689, 0.9162535493740466], [0.0, 0.9987509682522168, 0.04996502191793453], [-0.9173994103629876, -0.019884466838230128, 0.3974706653882801]], 'axis': [0.9162535493740466, 0.04996502191793453, 0.3974706653882801], 'zmin': -0.02094483702569304, 'zmax': 0.024868022005945133, 'profiles': [{'outer': [[-0.03214530693030579, -0.058627340149965144], [-0.03247689936690479, -0.05324878142632562], [-0.0323737488417809, -0.04473598773988805], [-0.03189158168598044, -0.034375404902200056], [-0.031106810708373643, -0.02347640408304377], [-0.02988879398986793, -0.01304589952073175], [-0.02820128038080428, -0.004049043109944405], [-0.024402221984485366, 0.011602869654515402], [-0.02270723816843029, 0.018255068604445455], [-0.021225007388050218, 0.023422410439466034], [-0.021014273745749122, 0.026945102400224366], [-0.022416440532043707, 0.028486113935370157], [-0.024632441288498133, 0.03129714952440869], [-0.025047456403865697, 0.03665064968562746], [-0.024510962553647146, 0.04297442918849412], [-0.02385452267073874, 0.04871662276422425], [-0.022849737360563154, 0.05673474481977447], [-0.021428179113206464, 0.05944849536617822], [-0.02087648421495612, 0.05994640341931858], [-0.020647877782832235, 0.06029070862717101], [-0.02002893603057278, 0.060711320890492054], [-0.01873451694088923, 0.06187954211373709], [-0.013723984024367404, 0.06279838750631937], [-0.006770631841080942, 0.06329248074649729], [0.0012456862853211825, 0.0651263462392442], [0.009699185756630348, 0.0663790086958692], [0.018043971577488688, 0.06519616654334119], [0.025027683275574447, 0.06305055919165031], [0.02951835878899399, 0.061009569735724356], [0.032404540844028065, 0.05910622075731408], [0.03298953981601836, 0.054670501216397244], [0.03274694296078029, 0.05023405896611398], [0.03215447715010803, 0.045022674858302233], [0.0307881729944901, 0.03443079642558387], [0.03031637445353211, 0.028672988160339443], [0.030124927859677433, 0.021526021380431033], [0.03046712381613339, 0.015113767474607447], [0.031628595993740544, 0.011629430543877895], [0.03185967387083318, 0.01080082225977935], [0.031481715549340025, 0.00915504112254318], [0.0286941437219492, 0.0057727902343327996], [0.02482295927039283, 0.0013875872502952002], [0.021203087063526575, -0.0033130642929226272], [0.017411780275788765, -0.00868826072306522], [0.013431438358669456, -0.014928801146824296], [0.009308179123140083, -0.022609811138050065], [0.0056626519537215985, -0.030930048439345437], [0.0026401792091044957, -0.03940027533639805], [0.00038881463602581434, -0.04743886372050126], [-0.0016761731009544971, -0.0543872395819268], [-0.003814158619923635, -0.05859213118757116], [-0.006876824839590119, -0.061725731309278824], [-0.008181913848237486, -0.06287906499435335], [-0.011688806764046463, -0.06527130329218003], [-0.015328569857395185, -0.06638361719118259], [-0.01683225358964514, -0.06664273588902024], [-0.020558878221793902, -0.06616839841228764], [-0.02407898707267585, -0.06512745773576367], [-0.02715568649823668, -0.06444646471730231], [-0.030672621360599266, -0.062319440193116936], [-0.031170993044715566, -0.060745691076321044]], 'holes': []}], 'simplify_tolerance': 2.660434891697789e-05, 'sketch_entity_count': 61}
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
