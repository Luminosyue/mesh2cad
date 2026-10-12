import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-43,0))
w1=cq.Workplane('XY',origin=(0,0,14))
r=w0.sketch().segment((-72,-68),(-38,-68)).segment((-38,-100)).segment((14,-100)).segment((14,-36)).segment((71,-36)).segment((71,50)).segment((14,50)).segment((14,100)).segment((-72,100)).close().assemble().reset().face(w0.sketch().segment((-71,-45),(-38,-45)).segment((-38,-36)).segment((-3,-36)).segment((-3,50)).segment((14,50)).segment((14,49)).segment((-71,49)).close().assemble(),mode='s').push([(64,47)]).circle(5,mode='s').finalize().extrude(86).union(w1.sketch().segment((-100,-10),(-87,-10)).segment((-87,3)).segment((-36,3)).segment((-36,-10)).segment((68,-10)).segment((68,43)).segment((-100,43)).close().assemble().finalize().extrude(-86))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0031_00313534.step')
