import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-20))
w1=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().arc((-71,38),(-64,-48),(18,-78)).segment((18,-77)).segment((19,-77)).arc((40,-69),(59,-54)).segment((60,-54)).segment((60,-53)).arc((79,-13),(72,34)).arc((69,29),(65,25)).arc((64,15),(60,6)).segment((60,4)).segment((59,4)).arc((40,-42),(-4,-65)).arc((-64,-40),(-64,25)).arc((-68,31),(-71,38)).assemble().reset().face(w0.sketch().arc((-56,57),(-12,67),(32,57)).arc((-12,79),(-56,57)).assemble()).finalize().extrude(-80).union(w0.sketch().segment((-68,43),(-67,41)).arc((-70,-10),(-39,-51)).segment((-39,-66)).segment((-25,-66)).segment((-25,-51)).arc((-1,-43),(18,-26)).segment((19,-25)).segment((19,-24)).arc((22,34),(-25,66)).segment((-25,81)).segment((-39,81)).segment((-39,66)).arc((-57,56),(-68,43)).assemble().finalize().extrude(-10)).union(w0.workplane(offset=86/2).moveTo(3,0).cylinder(86,37)).union(w1.sketch().arc((11,-39),(20,-34),(28,-27)).arc((27,-25),(26,-23)).arc((-28,29),(11,-37)).close().assemble().finalize().extrude(110))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__50001_e86a6698_0011.step')
