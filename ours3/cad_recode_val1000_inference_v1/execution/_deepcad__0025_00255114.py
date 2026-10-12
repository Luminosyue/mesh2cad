import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(100,0,0))
w1=cq.Workplane('YZ',origin=(2,0,0))
r=w0.sketch().segment((-50,-25),(50,-25)).arc((46,-6),(34,11)).segment((34,14)).segment((31,14)).arc((28,16),(24,19)).arc((23,19),(22,20)).arc((-10,24),(-36,10)).arc((-30,7),(-25,3)).arc((-19,-1),(-16,-7)).arc((1,-18),(19,-13)).arc((20,-18),(22,-23)).arc((-14,-25),(-50,-2)).close().assemble().finalize().extrude(-196).union(w0.workplane(offset=-34/2).moveTo(0,0).cylinder(34,25)).union(w1.sketch().arc((-48,-12),(-14,-23),(18,-12)).segment((18,-25)).segment((50,-25)).arc((-4,25),(-48,-12)).assemble().finalize().extrude(-102))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0025_00255114.step')
