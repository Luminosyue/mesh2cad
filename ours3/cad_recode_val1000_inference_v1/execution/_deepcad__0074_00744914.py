import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-47))
r=w0.sketch().segment((-43,-83),(-30,-83)).segment((-30,-100)).segment((43,-100)).segment((43,100)).segment((-30,100)).segment((-30,87)).segment((-43,87)).segment((-43,55)).arc((-40,56),(-37,56)).segment((-37,68)).segment((-30,68)).segment((-30,56)).arc((-25,56),(-20,55)).segment((-20,43)).arc((-32,29),(-43,15)).close().assemble().reset().face(w0.sketch().arc((20,43),(25,56),(30,68)).segment((30,79)).segment((20,79)).close().assemble()).finalize().extrude(94).union(w0.sketch().segment((-43,-29),(-21,-29)).segment((-21,21)).segment((43,21)).segment((43,100)).segment((-32,100)).segment((-32,74)).segment((-43,74)).close().assemble().finalize().extrude(94))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0074_00744914.step')
