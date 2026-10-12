import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().segment((-100,-100),(-66,-100)).segment((-100,-58)).close().assemble().reset().face(w0.sketch().segment((-100,-29),(-64,29)).segment((-64,35)).segment((-61,35)).segment((-34,100)).segment((-100,100)).close().assemble()).reset().face(w0.sketch().segment((-61,-100),(100,-100)).segment((100,100)).segment((66,100)).segment((100,58)).segment((100,52)).segment((97,52)).segment((70,-27)).segment((70,-35)).segment((67,-35)).segment((64,-43)).segment((64,-52)).segment((61,-52)).segment((34,-100)).segment((-34,-45)).segment((100,52)).segment((100,100)).segment((-100,100)).segment((-100,-29)).segment((-64,-87)).segment((-64,-79)).segment((-61,-79)).close().assemble()).finalize().extrude(20)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0023_00230605.step')
