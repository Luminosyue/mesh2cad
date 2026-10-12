import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-5))
r=w0.sketch().segment((-100,-6),(-63,-6)).segment((-63,-35)).segment((-56,-35)).segment((-56,-46)).segment((-40,-46)).segment((-40,-35)).segment((-32,-35)).segment((-32,-20)).segment((-15,-20)).segment((-15,-50)).segment((62,-50)).segment((62,-11)).segment((100,-11)).segment((100,11)).segment((62,11)).segment((62,48)).segment((44,48)).segment((44,50)).segment((-63,50)).segment((-63,21)).segment((-56,21)).segment((-56,26)).segment((-63,26)).segment((-63,11)).segment((-82,11)).segment((-82,0)).segment((-100,0)).close().assemble().reset().face(w0.sketch().segment((-56,0),(-40,0)).segment((-40,11)).segment((-22,11)).arc((-35,33),(-56,21)).close().assemble(),mode='s').push([(23,0)]).circle(15,mode='s').finalize().extrude(10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0051_00516442.step')
