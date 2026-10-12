import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-65,0))
r=w0.workplane(offset=107/2).cylinder(107,39).union(w0.sketch().arc((-39,-5),(0,32),(39,-5)).segment((39,5)).segment((-39,5)).close().assemble().reset().face(w0.sketch().arc((-25,-30),(0,-39),(25,-30)).segment((23,-30)).arc((0,-36),(-23,-30)).close().assemble()).finalize().extrude(200)).union(w1.sketch().arc((-12,37),(11,-38),(-5,39)).arc((-6,35),(-12,37)).assemble().finalize().extrude(105))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__34782_b461066c_0016.step')
