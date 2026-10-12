import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,9))
w1=cq.Workplane('YZ',origin=(98,0,0))
r=w0.workplane(offset=-20/2).moveTo(-45,-1).box(90,2,20).union(w0.sketch().segment((-100,-32),(-22,-32)).segment((-22,-31)).segment((-20,-31)).segment((-20,-32)).segment((32,-32)).segment((32,32)).segment((-100,32)).close().assemble().reset().face(w0.sketch().segment((-80,-18),(-72,-18)).arc((-73,0),(-70,18)).segment((-80,18)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-57,-26),(-22,-26)).segment((-22,-18)).segment((-19,-18)).segment((-19,18)).segment((-22,18)).segment((-22,26)).segment((-57,26)).arc((-51,0),(-57,-26)).assemble(),mode='s').push([(0,21)]).circle(6,mode='s').finalize().extrude(-14)).union(w1.sketch().arc((-28,10),(2,-11),(31,-1)).arc((25,3),(21,10)).segment((14,10)).arc((0,8),(-14,10)).close().assemble().finalize().extrude(2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00798021.step')
