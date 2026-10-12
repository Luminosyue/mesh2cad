import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-40))
w1=cq.Workplane('XY',origin=(0,0,-17))
r=w0.sketch().segment((-99,-16),(-99,16)).arc((-100,0),(-99,-16)).assemble().reset().face(w0.sketch().arc((-98,18),(-10,-14),(-71,-70)).segment((-71,-74)).arc((-51,-86),(-27,-96)).segment((-27,-63)).segment((-18,-63)).segment((-18,-98)).segment((-21,-98)).arc((-1,-100),(19,-98)).segment((22,-98)).segment((22,-97)).arc((88,-48),(91,34)).segment((91,18)).segment((88,18)).arc((60,-41),(-3,-61)).segment((-3,20)).segment((50,20)).arc((56,53),(71,70)).arc((49,80),(27,84)).segment((27,96)).segment((19,96)).arc((-1,98),(-18,98)).segment((-21,98)).segment((-21,97)).arc((-67,74),(-93,28)).segment((-31,28)).segment((-31,18)).segment((-18,18)).segment((-18,70)).arc((-14,70),(-11,68)).segment((-11,18)).close().assemble()).finalize().extrude(40).union(w0.sketch().segment((26,-21),(67,-21)).segment((67,-1)).arc((83,21),(67,42)).segment((67,43)).segment((26,43)).close().assemble().finalize().extrude(80)).union(w1.sketch().arc((48,-38),(61,-40),(73,-35)).arc((65,21),(90,-28)).arc((92,-23),(94,-18)).arc((61,40),(48,-26)).arc((49,-32),(48,-38)).assemble().finalize().extrude(53))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0099_00995261.step')
