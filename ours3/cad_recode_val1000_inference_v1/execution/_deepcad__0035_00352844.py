import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-4,0,0))
w1=cq.Workplane('YZ',origin=(-4,0,0))
r=w0.sketch().segment((-100,-10),(-98,-10)).segment((-98,-14)).segment((-62,-14)).segment((-62,-12)).segment((-60,-12)).segment((-60,-14)).segment((88,-14)).segment((88,-10)).segment((100,-10)).segment((100,10)).segment((88,10)).segment((88,14)).segment((-78,14)).arc((-88,10),(-98,12)).segment((-98,10)).segment((-100,10)).close().assemble().push([(49,0)]).circle(17,mode='s').finalize().extrude(8).union(w1.sketch().segment((-12,-13),(12,-13)).segment((12,-11)).arc((10,-9),(12,-7)).segment((12,13)).segment((-12,13)).close().assemble().finalize().extrude(2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0035_00352844.step')
