import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-85,0))
r=w0.sketch().segment((-100,-80),(100,-80)).segment((100,0)).segment((0,0)).segment((0,20)).arc((-10,13),(-20,10)).segment((-20,0)).segment((-24,0)).segment((-24,10)).arc((-34,13),(-44,20)).segment((-44,0)).segment((-100,0)).close().assemble().reset().face(w0.sketch().segment((-100,20),(-44,20)).arc((-34,27),(-24,27)).segment((-24,37)).segment((-20,37)).segment((-20,27)).arc((-10,27),(0,20)).segment((0,80)).segment((-100,80)).close().assemble()).finalize().extrude(133).union(w0.sketch().segment((-97,-72),(-26,-72)).segment((-26,-80)).segment((0,-80)).segment((0,-72)).segment((81,-72)).segment((81,-63)).segment((58,-63)).segment((58,-32)).segment((81,-32)).segment((81,0)).segment((0,0)).segment((0,80)).segment((-26,80)).segment((-26,0)).segment((-97,0)).close().assemble().push([(-49,-70)]).circle(2,mode='s').finalize().extrude(170))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0070_00704237.step')
