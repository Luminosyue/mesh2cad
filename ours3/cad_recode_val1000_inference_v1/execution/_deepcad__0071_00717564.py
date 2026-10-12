import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-8,0))
r=w0.sketch().segment((-100,-83),(15,-83)).segment((15,-69)).segment((100,-69)).segment((100,64)).segment((84,64)).segment((84,83)).segment((-100,83)).close().assemble().reset().face(w0.sketch().segment((-71,-14),(54,-14)).segment((54,-8)).segment((38,-8)).segment((38,21)).segment((54,21)).segment((54,64)).segment((15,64)).segment((15,71)).segment((-71,71)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-51,-64),(15,-64)).segment((15,-54)).arc((-18,-61),(-51,-54)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-51,21),(-18,27),(15,21)).segment((15,31)).segment((-51,31)).close().assemble(),mode='s').push([(24,-17)]).circle(17,mode='s').push([(77,-44)]).circle(14,mode='s').finalize().extrude(16)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0071_00717564.step')
