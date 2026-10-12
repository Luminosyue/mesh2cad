#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.03079722, -0.039124095, -0.11919316499999999], 'basis': [[0.0, 0.9208414353779923, -0.3899372396822325], [-0.9999924346367136, -0.0015167841552134837, -0.003581903846330738], [-0.003889816105918841, 0.3899342896653555, 0.9208344688780046]], 'axis': [-0.3899372396822325, -0.003581903846330738, 0.9208344688780046], 'zmin': -0.21128455054511444, 'zmax': 0.18952775387350318, 'profiles': [{'outer': [[-0.1802509324916858, -0.010123458231335251], [-0.17746804419584428, 0.009762815745879772], [-0.1847239857541284, 0.028653714634620877], [-0.18191577184292532, 0.039897732067012394], [-0.18054321945786533, 0.04399809902675135], [-0.1849394623960909, 0.05713953604090477], [-0.1827016278453951, 0.10317192824860713], [-0.17521630238747626, 0.1077482653169313], [-0.17392263701892335, 0.11657021095382707], [-0.11276448681600008, 0.1593097116411664], [0.08690438474139169, 0.19113360416647024], [0.1602476566235104, 0.14416696193520193], [0.18127761911272433, 0.051176921181464684], [0.18071030041789315, 0.0487039212089924], [0.18116047414994355, 0.0469034066131926], [0.17998635336585284, 0.04217794794552413], [0.18457594966763782, 0.021784200969113283], [0.1792815320923602, 0.005161749500850651], [0.18149769351083603, -0.0009947915138128944], [0.18108335280052734, -0.002090314162437531], [0.18462223046627707, -0.012940254558860968], [0.1798213614367668, -0.027972715909539904], [0.18149769351083603, -0.0330028622625634], [0.18038059579872046, -0.037661828753086664], [0.18127761911272433, -0.0410265726147739], [0.18039914408466456, -0.04437494128840375], [0.18141079669165072, -0.0488103324625306], [0.16063094299874897, -0.14358954645307395], [0.08741432878029072, -0.19162976581169605], [-0.10458704267400551, -0.14483476093902467], [-0.16339178499065518, -0.09964713230236572], [-0.1662422962699955, -0.0837162667684404], [-0.17108833745148966, -0.08053244110299651], [-0.17748190509251557, -0.037085905111623615], [-0.1754480981123254, -0.027659158724278994], [-0.1774357517077881, -0.024925001109874098]], 'holes': []}], 'simplify_tolerance': 7.655267399563327e-05, 'sketch_entity_count': 45}
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
