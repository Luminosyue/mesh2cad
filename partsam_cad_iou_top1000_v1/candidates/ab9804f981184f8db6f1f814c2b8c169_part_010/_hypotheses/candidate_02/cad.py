#!/usr/bin/env python3
import cadquery as cq
from pathlib import Path

SPEC = {'kind': 'extrusion', 'center': [-0.18945410000000001, -0.35459722000000005, 0.040308689999999994], 'basis': [[-0.0, 0.9492991600582686, 0.3143741476531837], [0.3256241732594333, -0.2972405318042309, 0.8975616770126991], [0.9454992849225803, 0.10236782192370697, -0.3091147541698482]], 'axis': [0.3143741476531837, 0.8975616770126991, -0.3091147541698482], 'zmin': -0.05424992819193751, 'zmax': 0.04921212383837312, 'profiles': [{'outer': [[-0.020020030040181696, 0.010587567311270675], [-0.020456054666704845, 0.018118051976918643], [-0.020060137157424194, 0.018761466941947243], [-0.0162908827438225, 0.023283862407092536], [-0.015488456856295532, 0.023513766999394177], [-0.013641313765487436, 0.02395558480557], [-0.012857043249697726, 0.024925642558438568], [-0.012319435611057614, 0.02518412731143493], [-0.00934811916995478, 0.02545354377332091], [-0.009086078664211716, 0.025045150627013894], [-0.008103760888864598, 0.025280111029719624], [-0.004227555792934619, 0.02404638146997265], [0.002788186761978085, 0.0178603731513714], [0.006663537838926354, 0.01301513387841527], [0.007862035014964673, 0.011774536269525395], [0.011777821091429148, 0.008446795311667197], [0.01859923580692297, 0.0018906268886225931], [0.02061248042836073, -0.002402937466608818], [0.02274123812849262, -0.006723555108854107], [0.023283340508376642, -0.011414591195812677], [0.022717837622019062, -0.012902676942506998], [0.02313043926210889, -0.014187209138584983], [0.026925402403570765, -0.018962560912102255], [0.02942783590638391, -0.021777714703356717], [0.02958415277814062, -0.024411448086848843], [0.028819981788403608, -0.026459097509914566], [0.028309864791318702, -0.02686259560633097], [0.026792328695126, -0.02655910894548055], [0.02368675075326102, -0.025553410319297497], [0.020063000815651252, -0.023756786777567436], [0.01820127974258494, -0.02281144791623319], [0.016131959382270186, -0.022117918677410704], [0.012738825822903426, -0.020464484261475093], [0.012281626342776408, -0.020523424997037697], [0.011329843889284874, -0.02028373127400101], [0.007878988906455574, -0.019278898991450997], [0.005867656712382324, -0.0191273645936516], [0.004868204115675089, -0.01950806388228408], [-0.0008949396646841136, -0.016203047683313206], [-0.005792104660148393, -0.010684784315721233], [-0.010346464691680084, -0.005825648542032321], [-0.014060776506708589, -0.0005242483796680106], [-0.01658029440459694, 0.004509674079958441]], 'holes': []}], 'simplify_tolerance': 1.0463227875930376e-05, 'sketch_entity_count': 85}
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
