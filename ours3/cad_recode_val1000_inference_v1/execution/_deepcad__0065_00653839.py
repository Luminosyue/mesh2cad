import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-25,0))
w1=cq.Workplane('YZ',origin=(-13,0,0))
r=w0.sketch().segment((-100,-37),(-62,-37)).segment((-62,-62)).segment((62,-62)).segment((62,-37)).segment((100,-37)).segment((100,62)).segment((-100,62)).close().assemble().push([(0,12)]).circle(31,mode='s').finalize().extrude(75).union(w0.sketch().segment((-86,-6),(-53,-6)).segment((-53,-59)).segment((53,-59)).segment((53,-6)).segment((86,-6)).segment((86,6)).segment((53,6)).segment((53,59)).segment((-53,59)).segment((-53,6)).segment((-86,6)).close().assemble().finalize().extrude(75)).union(w1.sketch().segment((-50,-63),(-35,-63)).segment((-35,-47)).segment((-40,-47)).segment((-40,-32)).segment((-35,-32)).segment((-35,-26)).segment((-40,-26)).segment((-40,-11)).segment((-35,-11)).segment((-35,63)).segment((-50,63)).close().assemble().finalize().extrude(-49))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00653839.step')
