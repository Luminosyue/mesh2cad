import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,19))
r=w0.sketch().segment((-68,-100),(68,-100)).segment((68,-12)).segment((68,100)).segment((-68,100)).segment((-68,52)).arc((-64,51),(-68,50)).close().assemble().reset().face(w0.sketch().segment((-68,-60),(-68,-45)).arc((-69,-52),(-68,-60)).assemble(),mode='s').reset().face(w0.sketch().arc((-60,-66),(-19,-91),(22,-66)).segment((-6,-66)).arc((-19,-68),(-32,-66)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-60,14),(-32,14)).arc((-19,16),(-6,14)).segment((22,14)).arc((-19,39),(-60,14)).assemble(),mode='s').reset().face(w0.sketch().arc((28,-60),(29,-52),(28,-45)).close().assemble(),mode='s').finalize().extrude(-38).union(w0.sketch().segment((-56,-27),(-46,-27)).arc((-19,-44),(9,-27)).segment((68,-27)).segment((68,65)).segment((-56,65)).close().assemble().finalize().extrude(-3))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0075_00751218.step')
