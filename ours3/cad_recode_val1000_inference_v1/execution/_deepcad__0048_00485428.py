import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-5,0))
r=w0.sketch().segment((-100,0),(-93,0)).segment((-93,-15)).segment((-15,-15)).segment((-15,-14)).segment((32,-15)).segment((32,-10)).segment((58,-10)).segment((58,-15)).segment((100,-15)).segment((100,15)).segment((-100,15)).close().assemble().reset().face(w0.sketch().segment((-87,10),(-86,10)).arc((-84,9),(-82,10)).segment((-81,10)).segment((-81,12)).segment((-82,12)).arc((-84,13),(-86,12)).segment((-87,12)).close().assemble(),mode='s').push([(-33,0)]).rect(10,26,mode='s').finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0048_00485428.step')
