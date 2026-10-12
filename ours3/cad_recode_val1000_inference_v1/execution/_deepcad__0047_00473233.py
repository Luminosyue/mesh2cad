import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
r=w0.sketch().segment((-100,-15),(-94,-16)).segment((-94,-19)).segment((-61,-19)).segment((-61,-14)).segment((-47,-14)).arc((-40,-1),(-32,-14)).segment((-31,-14)).segment((-31,-19)).segment((31,-19)).segment((31,-16)).segment((47,-16)).segment((47,-19)).segment((82,-19)).segment((82,-18)).arc((100,0),(82,18)).segment((82,16)).segment((67,16)).segment((67,18)).segment((47,18)).segment((47,16)).segment((31,16)).segment((31,19)).segment((-31,19)).segment((-31,16)).segment((-47,16)).segment((-47,19)).segment((-94,19)).segment((-94,16)).segment((-100,16)).close().assemble().push([(0,2)]).circle(10,mode='s').push([(87,2)]).circle(2,mode='s').finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0047_00473233.step')
