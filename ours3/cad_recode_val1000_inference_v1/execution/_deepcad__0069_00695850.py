import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-67))
w1=cq.Workplane('XY',origin=(0,0,39))
r=w0.sketch().arc((-96,29),(-96,-28),(-61,-79)).arc((-20,-98),(25,-97)).arc((35,-94),(44,-90)).arc((50,-87),(55,-83)).arc((50,-85),(45,-86)).arc((50,-79),(54,-71)).arc((56,-70),(58,-69)).arc((59,-14),(96,27)).arc((87,46),(74,62)).arc((65,75),(52,85)).segment((52,86)).segment((51,86)).arc((0,100),(-51,86)).segment((-52,86)).segment((-52,85)).arc((-79,61),(-94,29)).close().assemble().push([(0,-1)]).circle(75,mode='s').finalize().extrude(56).union(w0.sketch().arc((-30,33),(-34,-21),(8,-55)).arc((30,-69),(54,-65)).arc((55,-45),(74,-54)).arc((99,-10),(89,41)).segment((89,42)).segment((88,42)).arc((76,52),(61,58)).arc((30,69),(-1,61)).arc((-14,52),(-24,42)).segment((-25,42)).segment((-25,41)).arc((-28,37),(-30,33)).assemble().finalize().extrude(134)).union(w1.workplane(offset=-80/2).moveTo(31,0).cylinder(80,69))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0069_00695850.step')
