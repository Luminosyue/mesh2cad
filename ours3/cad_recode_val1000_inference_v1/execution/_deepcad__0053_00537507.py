import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,62,0))
r=w0.sketch().segment((-63,-100),(-12,-100)).segment((-12,-22)).segment((-63,22)).close().assemble().reset().face(w0.sketch().segment((-63,65),(-29,100)).segment((-63,100)).close().assemble()).reset().face(w0.sketch().segment((-27,100),(-12,83)).segment((-12,100)).close().assemble()).reset().face(w0.sketch().segment((-12,-100),(-10,-100)).segment((-12,-97)).close().assemble()).reset().face(w0.sketch().segment((-12,-89),(-12,-83)).arc((-13,-86),(-12,-89)).assemble()).reset().face(w0.sketch().segment((-12,100),(-10,97)).segment((-12,97)).close().assemble()).reset().face(w0.sketch().segment((-10,10),(-12,7)).segment((-12,10)).close().assemble()).finalize().extrude(-125).union(w0.sketch().segment((-62,-96),(21,-96)).segment((21,-30)).arc((15,31),(49,-17)).segment((62,-17)).segment((62,100)).segment((-62,100)).close().assemble().finalize().extrude(-50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00537507.step')
