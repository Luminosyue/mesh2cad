import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,12))
r=w0.sketch().segment((-100,-44),(-34,-44)).segment((-34,-34)).segment((-25,-34)).segment((-25,-44)).segment((-1,-44)).segment((-1,-45)).segment((25,-45)).segment((25,-44)).segment((100,-44)).segment((100,45)).segment((56,45)).segment((56,39)).segment((39,39)).segment((39,45)).segment((-25,45)).segment((-25,44)).segment((-75,44)).segment((-75,37)).segment((-100,37)).close().assemble().push([(-43,10)]).circle(24,mode='s').push([(6,0)]).circle(12,mode='s').push([(62,-26)]).circle(2,mode='s').push([(66,20)]).circle(10,mode='s').finalize().extrude(-24).union(w0.sketch().segment((-97,37),(-53,-33)).segment((-46,-29)).segment((-90,41)).close().assemble().finalize().extrude(-1))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0078_00789229.step')
