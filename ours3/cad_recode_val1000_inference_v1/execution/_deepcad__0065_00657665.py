import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
w1=cq.Workplane('YZ',origin=(-12,0,0))
r=w0.sketch().segment((-28,-100),(28,-100)).segment((28,-12)).segment((25,-12)).segment((25,12)).segment((28,12)).segment((28,100)).segment((-28,100)).segment((-28,53)).arc((-26,52),(-28,51)).close().assemble().finalize().extrude(56).union(w0.workplane(offset=66/2).moveTo(0,0).box(56,124,66)).union(w1.sketch().arc((20,41),(27,43),(20,44)).arc((21,43),(20,41)).assemble().finalize().extrude(102))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00657665.step')
