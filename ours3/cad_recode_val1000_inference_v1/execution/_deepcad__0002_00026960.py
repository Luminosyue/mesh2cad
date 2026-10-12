import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,39))
r=w0.sketch().arc((-39,-10),(-38,-12),(-37,-14)).arc((30,26),(-39,-10)).assemble().finalize().extrude(-200).union(w0.sketch().arc((-26,-30),(26,0),(-26,30)).close().assemble().finalize().extrude(-119)).union(w1.sketch().arc((-30,27),(-39,-9),(-13,-38)).arc((-11,-36),(-9,-39)).arc((18,-36),(37,-16)).arc((35,-14),(38,-14)).arc((35,19),(7,40)).arc((-10,18),(-30,27)).assemble().finalize().extrude(-139))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0002_00026960.step')
