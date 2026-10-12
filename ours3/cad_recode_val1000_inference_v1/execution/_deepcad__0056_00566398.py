import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,51))
r=w0.sketch().arc((-98,-11),(-60,-71),(6,-99)).close().assemble().reset().face(w0.sketch().segment((-97,17),(-10,46)).segment((-10,59)).segment((10,59)).segment((10,39)).segment((79,61)).arc((63,76),(42,89)).segment((42,90)).segment((40,90)).arc((0,99),(-40,90)).segment((-42,90)).segment((-42,89)).arc((-74,66),(-97,31)).close().assemble()).reset().face(w0.sketch().arc((14,-97),(84,-52),(95,26)).close().assemble()).finalize().extrude(-200).union(w0.sketch().segment((-100,-7),(-12,-38)).arc((-39,6),(-12,50)).segment((-72,71)).close().assemble().reset().face(w0.sketch().segment((12,-50),(72,-71)).segment((100,7)).segment((12,38)).arc((39,-6),(12,-50)).assemble()).finalize().extrude(-137)).union(w1.workplane(offset=-95/2).cylinder(95,40))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0056_00566398.step')
