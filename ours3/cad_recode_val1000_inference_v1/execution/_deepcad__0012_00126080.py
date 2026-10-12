import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,42,0))
w1=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-28,-73),(-28,97)).arc((-46,12),(-28,-73)).assemble().reset().face(w0.sketch().arc((-24,-75),(16,-91),(59,-75)).close().assemble()).reset().face(w0.sketch().segment((-24,98),(59,98)).arc((16,100),(-24,98)).assemble()).reset().face(w0.sketch().arc((60,13),(63,44),(60,75)).close().assemble()).finalize().extrude(-56).union(w0.sketch().segment((-15,-100),(35,-100)).segment((35,-8)).arc((27,1),(35,10)).segment((35,32)).segment((-15,32)).close().assemble().finalize().extrude(-34)).union(w1.sketch().segment((-43,-62),(14,-62)).segment((14,-39)).segment((-42,-39)).segment((-42,-50)).segment((-43,-50)).close().assemble().finalize().extrude(200))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0012_00126080.step')
