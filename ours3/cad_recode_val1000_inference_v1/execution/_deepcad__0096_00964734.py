import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(14,0,0))
r=w0.sketch().segment((-100,-10),(-93,-10)).segment((-93,-18)).segment((100,-18)).segment((100,18)).segment((-93,18)).segment((-93,13)).segment((-100,13)).close().assemble().reset().face(w0.sketch().segment((-70,13),(-58,13)).arc((-64,15),(-70,13)).assemble(),mode='s').reset().face(w0.sketch().arc((-67,-10),(-64,-11),(-61,-10)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-70,13),(-61,13)).arc((-64,14),(-70,13)).assemble(),mode='s').reset().face(w0.sketch().arc((-58,-10),(-52,-11),(-46,-10)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-58,13),(-46,13)).arc((-52,14),(-58,13)).assemble(),mode='s').push([(33,0)]).circle(3,mode='s').push([(62,0)]).rect(4,10,mode='s').finalize().extrude(-28)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0096_00964734.step')
