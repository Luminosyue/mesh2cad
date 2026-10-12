import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,24))
w1=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-100,-39),(-95,-39)).segment((-95,-51)).segment((14,-51)).segment((14,51)).segment((-95,51)).segment((-95,49)).segment((-100,49)).close().assemble().reset().face(w0.sketch().segment((-95,-28),(-95,15)).arc((-100,-6),(-95,-28)).assemble(),mode='s').reset().face(w0.sketch().arc((-49,-39),(-19,-48),(10,-39)).close().assemble(),mode='s').reset().face(w0.sketch().segment((-49,49),(10,49)).arc((-19,58),(-49,49)).assemble(),mode='s').reset().face(w0.sketch().arc((13,-28),(18,-6),(13,15)).close().assemble(),mode='s').finalize().extrude(-48).union(w0.workplane(offset=-1/2).moveTo(-19,-6).cylinder(1,15)).union(w1.workplane(offset=-11/2).moveTo(84,44).cylinder(11,5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0062_00629651.step')
