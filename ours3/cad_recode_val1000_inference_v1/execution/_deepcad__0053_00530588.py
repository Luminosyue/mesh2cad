import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(67,0,0))
w1=cq.Workplane('YZ',origin=(16,0,0))
r=w0.sketch().segment((-95,-100),(95,-100)).segment((95,100)).segment((34,100)).segment((-10,20)).segment((4,46)).segment((4,35)).segment((5,35)).segment((5,28)).segment((4,28)).segment((4,13)).segment((-10,13)).segment((-10,28)).segment((-11,28)).segment((-11,35)).segment((-10,35)).segment((-10,36)).segment((-95,-27)).close().assemble().finalize().extrude(-134).union(w0.sketch().segment((-85,-67),(88,-67)).segment((88,68)).segment((43,68)).segment((43,58)).segment((42,58)).segment((42,68)).segment((16,68)).segment((16,43)).segment((-2,43)).segment((-2,68)).segment((-85,68)).close().assemble().finalize().extrude(-3)).union(w1.workplane(offset=-66/2).moveTo(-21,-18).cylinder(66,18))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00530588.step')
