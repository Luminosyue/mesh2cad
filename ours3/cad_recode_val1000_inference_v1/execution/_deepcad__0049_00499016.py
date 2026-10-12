import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(73,0,0))
r=w0.sketch().arc((-26,32),(-34,-23),(20,-36)).arc((-21,-15),(-26,32)).assemble().finalize().extrude(-200).union(w0.workplane(offset=-105/2).moveTo(0,1).cylinder(105,36)).union(w1.sketch().arc((33,-24),(41,-2),(33,24)).close().assemble().finalize().extrude(-123))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0049_00499016.step')
