import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-25,0))
r=w0.sketch().segment((-63,-88),(44,-88)).segment((44,-26)).segment((57,-26)).segment((57,-10)).segment((63,-10)).segment((63,100)).segment((-63,100)).segment((-63,19)).arc((-59,17),(-63,15)).close().assemble().finalize().extrude(30).union(w0.sketch().segment((-63,-100),(63,-100)).segment((63,-46)).arc((-19,-10),(63,26)).segment((63,100)).segment((-63,100)).close().assemble().finalize().extrude(50))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00029714.step')
