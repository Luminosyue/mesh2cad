import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-4))
w1=cq.Workplane('XY',origin=(0,0,43))
r=w0.sketch().arc((-61,39),(-61,-39),(10,-71)).arc((40,-60),(63,-36)).arc((68,24),(28,67)).arc((24,68),(21,69)).arc((-24,68),(-60,41)).segment((-60,39)).close().assemble().push([(24,0)]).circle(52,mode='s').finalize().extrude(-96).union(w0.sketch().segment((-42,38),(-38,38)).segment((-38,64)).arc((-40,60),(-42,57)).close().assemble().finalize().extrude(-12)).union(w0.sketch().segment((-29,-14),(-27,-14)).arc((22,-51),(69,-14)).segment((71,-14)).segment((71,-10)).arc((72,0),(71,10)).segment((71,14)).segment((69,14)).arc((22,51),(-27,14)).segment((-29,14)).segment((-29,10)).arc((-30,0),(-29,-10)).close().assemble().finalize().extrude(104)).union(w1.workplane(offset=57/2).moveTo(22,0).cylinder(57,51))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00648240.step')
