import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,3))
r=w0.sketch().segment((-100,-6),(-91,-6)).segment((-93,4)).segment((-80,6)).segment((-100,6)).close().assemble().reset().face(w0.sketch().segment((-77,-6),(-33,-6)).segment((-33,6)).segment((-45,6)).segment((-45,4)).segment((-40,-6)).segment((-53,-6)).segment((-53,0)).segment((-57,-4)).segment((-60,-1)).segment((-57,3)).segment((-53,0)).segment((-53,6)).segment((-77,6)).close().assemble()).reset().face(w0.sketch().segment((-33,-6),(100,-6)).segment((100,6)).segment((-33,6)).segment((-33,0)).segment((-29,-4)).segment((-33,-8)).close().assemble()).finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0016_00161164.step')
