import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,72))
w1=cq.Workplane('XY',origin=(0,0,67))
r=w0.sketch().segment((-95,-13),(-95,-11)).segment((-74,-11)).arc((-68,-10),(-63,-11)).segment((-53,-11)).arc((-99,5),(-52,-13)).segment((-63,-13)).arc((-68,-14),(-74,-13)).close().assemble().finalize().extrude(-144).union(w0.sketch().push([(-4,-2)]).circle(9).reset().face(w0.sketch().segment((38,2),(58,-6)).arc((59,-3),(59,0)).segment((59,7)).segment((46,11)).close().assemble()).reset().face(w0.sketch().segment((78,0),(89,-4)).segment((94,10)).segment((82,10)).arc((80,6),(78,2)).close().assemble()).reset().face(w0.sketch().arc((84,-10),(99,-4),(92,11)).segment((93,10)).close().assemble()).finalize().extrude(-145)).union(w1.sketch().push([(-81,3)]).circle(15).circle(10,mode='s').finalize().extrude(-130))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0078_00783050.step')
