import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(46,0,0))
r=w0.workplane(offset=-101/2).cylinder(101,29).union(w0.workplane(offset=-35/2).cylinder(35,26)).union(w1.sketch().arc((-29,4),(0,-29),(29,4)).segment((29,-8)).segment((25,-8)).arc((0,-14),(-25,-8)).segment((-29,-8)).close().assemble().reset().face(w1.sketch().segment((-29,8),(-25,8)).arc((-25,10),(-24,11)).arc((-27,12),(-29,8)).assemble()).finalize().extrude(-146))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0040_00404770.step')
