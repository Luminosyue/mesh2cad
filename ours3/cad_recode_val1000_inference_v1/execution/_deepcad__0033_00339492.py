import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-88,0))
w1=cq.Workplane('XY',origin=(0,0,-39))
r=w0.sketch().segment((-36,37),(-17,37)).segment((-17,55)).segment((17,55)).segment((17,37)).segment((36,37)).arc((0,60),(-36,37)).assemble().reset().face(w0.sketch().arc((-17,-37),(0,-50),(17,-37)).close().assemble()).reset().face(w0.sketch().segment((17,-32),(52,-41)).segment((57,-17)).segment((57,1)).segment((42,5)).segment((42,37)).segment((17,37)).close().assemble()).finalize().extrude(-6).union(w0.sketch().segment((-74,-65),(-39,-65)).arc((-60,-54),(-74,-35)).close().assemble().reset().face(w0.sketch().arc((-74,-19),(-60,0),(-39,11)).segment((-74,11)).close().assemble()).reset().face(w0.sketch().segment((-43,65),(-39,53)).arc((-39,60),(-43,65)).assemble()).reset().face(w0.sketch().segment((-19,42),(65,42)).segment((65,-65)).segment((58,-65)).segment((74,-31)).close().assemble()).finalize().extrude(188)).union(w1.sketch().segment((-65,-62),(-37,-62)).segment((-37,-100)).segment((65,-100)).segment((65,63)).segment((1,63)).arc((11,1),(-37,-39)).segment((-37,-54)).arc((-54,-47),(-65,-34)).close().assemble().finalize().extrude(43))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00339492.step')
