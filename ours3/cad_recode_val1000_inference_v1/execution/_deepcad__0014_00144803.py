import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-7))
r=w0.sketch().segment((-80,-98),(-69,-98)).segment((-69,-100)).segment((-38,-100)).segment((-38,-98)).segment((-24,-98)).segment((-24,-75)).arc((-10,-73),(3,-68)).arc((10,-80),(19,-90)).segment((19,-100)).segment((60,-100)).segment((60,-90)).arc((79,-77),(69,-56)).arc((78,-19),(60,14)).segment((60,24)).segment((3,24)).arc((-10,29),(-24,31)).segment((-24,55)).segment((-38,55)).segment((-38,60)).segment((-69,60)).segment((-69,55)).segment((-80,55)).close().assemble().push([(-57,-70)]).circle(13,mode='s').push([(29,-43)]).circle(16,mode='s').finalize().extrude(7).union(w0.sketch().segment((-1,60),(10,53)).segment((10,87)).close().assemble().reset().face(w0.sketch().segment((12,73),(32,73)).segment((32,27)).segment((80,41)).segment((74,61)).segment((80,61)).segment((80,62)).segment((73,62)).segment((74,64)).segment((47,100)).close().assemble()).finalize().extrude(14))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0014_00144803.step')
