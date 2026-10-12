import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,4))
r=w0.sketch().segment((-48,-87),(-33,-87)).segment((-33,-100)).segment((48,-100)).segment((48,16)).segment((40,16)).arc((44,12),(48,6)).segment((48,100)).segment((-48,100)).segment((-48,55)).segment((-33,55)).segment((-33,36)).segment((-48,36)).close().assemble().reset().face(w0.sketch().segment((-40,-24),(-13,-54)).segment((40,1)).segment((13,31)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-33,64),(33,55)).segment((33,70)).segment((-33,79)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-33,-39),(33,-48)).segment((33,-33)).segment((-33,-24)).close().assemble(),mode='s').reset().face(w0.sketch().arc((-10,55),(19,52),(40,36)).segment((40,55)).close().assemble(),mode='s').finalize().extrude(-8)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0093_00932313.step')
