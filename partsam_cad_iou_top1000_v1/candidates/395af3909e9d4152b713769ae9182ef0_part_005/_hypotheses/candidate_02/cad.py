#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [0.16500814, -0.067604345, -0.20293985000000003], 'basis': [[0.0, 0.7132614515889842, 0.7008980679650753], [-0.999715612924178, -0.016714520005822932, 0.01700935320963166], [0.02384729073993651, -0.7006987416130773, 0.7130586092504704]], 'axis': [0.7008980679650753, 0.01700935320963166, 0.7130586092504704], 'zmin': -0.07187820562657166, 'zmax': 0.06803028668888021, 'profiles': [{'outer': [[-0.12927946376560517, 0.0030651615695294755], [-0.1305356440491138, 0.006057459769061581], [-0.13132320847533457, 0.008315417906978104], [-0.1316859991319743, 0.009776809317085276], [-0.13115206790362, 0.013130315762892114], [-0.13096900806543163, 0.013803766797681328], [-0.12644276673171792, 0.017112581204915014], [-0.1186730245991045, 0.020581929785565552], [-0.06577926694154311, 0.041973628017150884], [-0.029218495107801855, 0.05815637052991241], [0.013136796122726066, 0.06997729446534114], [0.1040592622392001, 0.0709645368063941], [0.11092176912398401, 0.0703969500983624], [0.12065246804243093, 0.06720411841827963], [0.13046170188031214, 0.061220374467122], [0.13068403279508256, 0.05991754422891665], [0.13120821866199964, 0.050636908191729134], [0.13177095772843728, 0.033753157924921125], [0.13228625666398725, 0.011849275154050697], [0.13267603681556497, -0.011744819879668918], [0.1328804972860736, -0.03343445888995912], [0.1328859657025332, -0.042493791827574255], [0.13271612542548644, -0.05534158515313606], [0.13256162838062463, -0.058641310182117386], [0.13236158203785198, -0.059645516490901204], [0.12236424475134795, -0.06560654271473795], [0.1124270943825068, -0.06840849119572458], [0.10646706133495142, -0.06814744876950565], [0.04729398373658545, -0.038147861617399234], [0.03494915188263538, -0.0313839868646643], [0.008932428924869704, -0.03203234049560885], [-0.07752003119948088, -0.046178027987310556], [-0.08061931076980468, -0.04642562120883012], [-0.08993754157893216, -0.04420185249243738], [-0.09727088639421509, -0.041518870829459924], [-0.10236909704079082, -0.03785344399097825], [-0.10441543888534452, -0.03624125604146164], [-0.10701468260563918, -0.03357790047035256], [-0.10981317760642005, -0.03012020261642266], [-0.11251889620177975, -0.02625498500678728], [-0.11779314493756254, -0.01800337199031003], [-0.12311385983190724, -0.008978068694961835], [-0.12553995799959172, -0.004596948484595094], [-0.1276073637346213, -0.0005302236095204594]], 'holes': []}], 'simplify_tolerance': 5.291439296690151e-05, 'sketch_entity_count': 44}
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
