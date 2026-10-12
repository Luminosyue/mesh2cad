import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-100,5),(-96,-5)).segment((-53,-5)).segment((-53,5)).close().assemble().reset().face(w0.sketch().segment((-53,5),(-1,5)).segment((-1,-5)).segment((100,-6)).arc((99,0),(96,5)).close().assemble()).finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0009_00097177.step')
