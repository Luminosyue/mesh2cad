import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,30))
r=w0.sketch().segment((-100,-100),(-51,-100)).segment((-100,-47)).close().assemble().reset().face(w0.sketch().segment((-100,-34),(-51,74)).segment((100,-10)).segment((100,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-46,-100),(100,-100)).segment((100,-34)).close().assemble()).reset().face(w0.sketch().segment((-46,-34),(46,-34)).arc((0,20),(-46,-34)).assemble()).finalize().extrude(-60)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00300419.step')
