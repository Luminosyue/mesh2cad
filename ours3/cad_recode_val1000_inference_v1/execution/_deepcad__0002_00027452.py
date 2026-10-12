import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,16))
r=w0.sketch().segment((-81,-100),(-53,-100)).segment((-81,-48)).close().assemble().reset().face(w0.sketch().segment((-81,-23),(-12,17)).segment((-12,16)).segment((12,16)).segment((12,3)).segment((20,-23)).segment((-53,-63)).segment((-53,-62)).segment((-81,-62)).close().assemble()).reset().face(w0.sketch().segment((-81,16),(-53,16)).segment((-53,28)).segment((-12,28)).segment((-12,16)).segment((12,16)).segment((12,5)).segment((20,-20)).segment((81,-56)).segment((81,100)).segment((-81,100)).close().assemble()).reset().face(w0.sketch().segment((-22,-100),(81,-100)).segment((81,-62)).segment((12,-100)).segment((12,-99)).close().assemble()).finalize().extrude(-32)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00027452.step')
