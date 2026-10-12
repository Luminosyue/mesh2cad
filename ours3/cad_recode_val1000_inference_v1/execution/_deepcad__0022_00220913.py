import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-37))
w1=cq.Workplane('ZX',origin=(0,39,0))
r=w0.sketch().segment((-100,-48),(-51,-48)).arc((-53,-44),(-54,-39)).segment((-90,-39)).segment((-90,39)).segment((-54,39)).arc((-53,44),(-51,48)).segment((-100,48)).close().assemble().reset().face(w0.sketch().segment((-34,-48),(100,-48)).segment((100,48)).segment((-20,48)).arc((-17,44),(-15,39)).segment((90,39)).segment((90,-39)).segment((-15,-39)).arc((-17,-44),(-20,-48)).close().assemble()).finalize().extrude(74).union(w1.sketch().arc((-36,-36),(36,0),(-36,36)).segment((-36,19)).segment((-15,19)).segment((-15,-36)).close().assemble().finalize().extrude(9))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0022_00220913.step')
