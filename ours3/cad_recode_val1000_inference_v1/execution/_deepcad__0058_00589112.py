import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().arc((-61,-56),(21,-79),(77,-19)).close().assemble().reset().face(w0.sketch().segment((-77,31),(-1,65)).segment((65,45)).arc((66,50),(67,55)).arc((64,53),(61,51)).segment((-13,83)).segment((-13,82)).arc((-73,40),(-61,-32)).close().assemble()).finalize().extrude(-200).union(w0.sketch().arc((70,45),(-79,-25),(81,17)).arc((77,31),(70,45)).assemble().finalize().extrude(-186))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00589112.step')
