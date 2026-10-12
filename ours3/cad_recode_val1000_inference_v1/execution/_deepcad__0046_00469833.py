import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-63,0))
r=w0.workplane(offset=5/2).moveTo(0,13).cylinder(5,65).union(w0.sketch().segment((-75,-100),(75,-100)).segment((75,97)).segment((6,100)).segment((-75,100)).close().assemble().reset().face(w0.sketch().segment((-75,-62),(-70,-62)).arc((-73,-58),(-75,-53)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-75,-49),(-73,-44),(-70,-40)).segment((-75,-40)).close().assemble(),mode='s').reset().face(w0.sketch().segment((70,-62),(75,-62)).segment((75,-53)).arc((73,-58),(70,-62)).assemble(),mode='s').reset().face(w0.sketch().arc((70,62),(73,58),(75,53)).segment((75,62)).close().assemble(),mode='s').finalize().extrude(126))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0046_00469833.step')
