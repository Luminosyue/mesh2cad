import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('XY',origin=(0,0,-83))
r=w0.sketch().segment((0,-18),(67,-18)).segment((67,83)).segment((0,83)).segment((0,61)).segment((28,80)).segment((67,24)).segment((0,24)).close().assemble().finalize().extrude(-200).union(w0.sketch().segment((-67,-83),(42,-83)).segment((42,-73)).arc((-14,-64),(-55,-25)).segment((-67,-25)).close().assemble().finalize().extrude(-195)).union(w1.sketch().segment((-100,-37),(-56,-37)).segment((-56,-67)).segment((100,-67)).segment((100,67)).segment((-100,67)).close().assemble().push([(32,15)]).circle(29,mode='s').finalize().extrude(66))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00359882.step')
