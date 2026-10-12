import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,11,0))
r=w0.sketch().arc((-92,-39),(-78,-62),(-56,-82)).segment((-56,-83)).segment((-54,-83)).arc((-44,-90),(-34,-95)).segment((-34,-83)).segment((-22,-83)).segment((-22,-98)).arc((26,-96),(66,-71)).segment((75,-67)).segment((73,-62)).arc((99,13),(52,83)).segment((52,84)).segment((50,84)).arc((30,95),(9,100)).segment((9,98)).arc((30,95),(50,84)).segment((49,84)).segment((49,83)).segment((22,83)).segment((22,98)).arc((10,99),(-2,100)).segment((-22,98)).segment((-22,93)).arc((-30,95),(-39,93)).segment((-39,92)).arc((-95,30),(-92,-39)).assemble().push([(-25,-28)]).circle(36,mode='s').reset().face(w0.sketch().arc((-73,-34),(-57,-1),(-31,24)).arc((-66,10),(-73,-34)).assemble(),mode='s').reset().face(w0.sketch().arc((9,-66),(17,-64),(22,-59)).arc((15,-57),(9,-54)).close().assemble(),mode='s').finalize().extrude(-22)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0038_00387798.step')
