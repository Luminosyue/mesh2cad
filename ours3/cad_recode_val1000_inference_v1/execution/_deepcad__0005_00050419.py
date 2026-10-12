import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-3))
w1=cq.Workplane('XY',origin=(0,0,31))
r=w0.sketch().segment((-100,-19),(-49,-19)).segment((-49,-18)).segment((-47,-18)).segment((-47,-19)).segment((43,-19)).segment((43,19)).segment((-100,19)).close().assemble().push([(29,16)]).circle(3,mode='s').finalize().extrude(-64).union(w0.sketch().segment((-93,-19),(-86,-19)).arc((-88,-16),(-90,-13)).segment((-93,-13)).close().assemble().reset().face(w0.sketch().arc((-93,13),(-88,16),(-86,19)).segment((-93,19)).close().assemble()).reset().face(w0.sketch().segment((-25,-19),(-18,-19)).segment((-18,-13)).segment((-22,-13)).arc((-23,-16),(-25,-19)).assemble()).finalize().extrude(-44)).union(w1.workplane(offset=35/2).moveTo(92,0).cylinder(35,8))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0005_00050419.step')
