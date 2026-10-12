import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(0,0,0))
w1=cq.Workplane('XY',origin=(0,0,-44))
r=w0.sketch().segment((-63,-95),(-59,-95)).segment((-59,-93)).arc((-60,-92),(-59,-91)).segment((-59,-79)).segment((-63,-79)).close().assemble().push([(62,-67)]).rect(4,54).finalize().extrude(1).union(w1.sketch().segment((-6,0),(-5,0)).segment((-5,-1)).segment((5,-1)).segment((5,0)).segment((6,0)).segment((6,10)).segment((5,10)).segment((5,11)).segment((-5,11)).segment((-5,10)).segment((-6,10)).close().assemble().finalize().extrude(144))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00175796.step')
