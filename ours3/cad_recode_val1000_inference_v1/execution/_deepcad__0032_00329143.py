import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
r=w0.sketch().segment((-100,-100),(16,-100)).segment((-19,-46)).segment((100,-46)).segment((100,62)).segment((29,-51)).segment((-100,-5)).close().assemble().reset().face(w0.sketch().segment((-100,15),(100,62)).segment((100,100)).segment((-100,100)).close().assemble()).finalize().extrude(34)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0032_00329143.step')
