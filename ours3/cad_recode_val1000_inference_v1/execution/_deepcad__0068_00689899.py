import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
w1=cq.Workplane('XY',origin=(0,0,28))
r=w0.sketch().arc((-10,32),(-99,-9),(1,-10)).arc((-36,4),(-10,32)).assemble().finalize().extrude(-46).union(w0.sketch().segment((-78,-18),(-78,15)).arc((-82,0),(-78,-18)).assemble().reset().face(w0.sketch().arc((-68,-36),(-54,-39),(-39,-36)).close().assemble()).reset().face(w0.sketch().segment((-68,30),(-39,30)).arc((-54,33),(-68,30)).assemble()).reset().face(w0.sketch().arc((-39,-18),(-35,0),(-39,15)).close().assemble()).reset().face(w0.sketch().segment((17,-4),(20,-25)).segment((28,-24)).arc((62,-50),(97,-24)).segment((97,-23)).arc((100,-7),(97,8)).segment((97,9)).segment((28,29)).segment((27,28)).arc((27,26),(26,24)).segment((26,23)).arc((23,10),(17,-4)).assemble()).push([(62,-7)]).circle(18,mode='s').finalize().extrude(47)).union(w1.sketch().arc((-68,30),(-65,32),(-62,35)).segment((-68,35)).close().assemble().finalize().extrude(-44))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00689899.step')
