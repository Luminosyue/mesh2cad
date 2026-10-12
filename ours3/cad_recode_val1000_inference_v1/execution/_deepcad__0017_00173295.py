import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,41,0))
w1=cq.Workplane('XY',origin=(0,0,-32))
r=w0.sketch().segment((-83,-48),(-40,50)).segment((-83,59)).segment((-83,25)).arc((-79,17),(-83,9)).close().assemble().reset().face(w0.sketch().arc((-63,-71),(-54,-82),(-43,-91)).segment((-40,-100)).segment((-29,-98)).arc((-15,-99),(-1,-99)).segment((-29,-84)).segment((19,-56)).arc((14,-53),(9,-51)).segment((-11,-86)).close().assemble()).reset().face(w0.sketch().segment((-54,64),(-27,76)).segment((-22,100)).arc((-35,89),(-50,77)).arc((-51,70),(-54,64)).assemble()).reset().face(w0.sketch().arc((28,-98),(41,-94),(53,-91)).segment((47,-73)).close().assemble()).finalize().extrude(-82).union(w0.sketch().segment((-83,-48),(-11,-24)).segment((-16,-17)).segment((-83,-4)).close().assemble().finalize().extrude(-69)).union(w0.workplane(offset=-47/2).moveTo(66,-89).cylinder(47,8)).union(w1.workplane(offset=-42/2).moveTo(-59,-10).cylinder(42,2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00173295.step')
