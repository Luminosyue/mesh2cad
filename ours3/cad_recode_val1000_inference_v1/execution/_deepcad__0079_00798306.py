import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-67))
w1=cq.Workplane('XY',origin=(0,0,39))
r=w0.sketch().arc((-96,29),(-96,-28),(-61,-79)).arc((-20,-98),(25,-97)).arc((35,-94),(44,-90)).arc((50,-87),(55,-83)).arc((50,-85),(45,-86)).arc((50,-79),(54,-71)).arc((56,-70),(58,-69)).arc((59,-14),(96,27)).arc((86,51),(69,72)).arc((56,83),(40,91)).arc((-41,91),(-93,34)).arc((-90,30),(-96,29)).assemble().push([(0,-1)]).circle(75,mode='s').finalize().extrude(56).union(w0.sketch().arc((-30,33),(-34,-21),(6,-63)).segment((6,-65)).segment((12,-65)).arc((32,-69),(52,-65)).segment((58,-65)).segment((58,-63)).arc((100,0),(58,63)).segment((58,65)).segment((52,65)).arc((32,69),(12,65)).segment((6,65)).segment((6,63)).arc((-10,55),(-22,42)).arc((-30,39),(-30,33)).assemble().finalize().extrude(134)).union(w1.sketch().arc((-27,-37),(99,-10),(-14,52)).arc((-12,48),(-10,44)).arc((98,-10),(-21,-37)).close().assemble().finalize().extrude(-90))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00798306.step')
