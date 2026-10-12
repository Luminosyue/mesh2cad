import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-80,0))
r=w0.sketch().segment((-100,-80),(-20,-80)).segment((-20,0)).segment((100,0)).segment((100,80)).segment((-100,80)).close().assemble().reset().face(w0.sketch().segment((-100,59),(-99,57)).segment((-97,58)).segment((-98,60)).close().assemble(),mode='s').push([(70,78)]).circle(2,mode='s').finalize().extrude(160)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0073_00738814.step')
