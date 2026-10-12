import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(3,0,0))
r=w0.sketch().segment((-20,-73),(-19,-73)).arc((0,-100),(19,-73)).segment((20,-73)).segment((20,-12)).segment((20,73)).segment((19,73)).arc((0,91),(-19,73)).segment((-20,73)).segment((-20,-12)).close().assemble().reset().face(w0.sketch().segment((-20,-15),(-20,-10)).arc((-21,-12),(-20,-15)).assemble(),mode='s').reset().face(w0.sketch().arc((20,-15),(21,-12),(20,-10)).close().assemble(),mode='s').finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__56343_60e8809c_0003.step')
