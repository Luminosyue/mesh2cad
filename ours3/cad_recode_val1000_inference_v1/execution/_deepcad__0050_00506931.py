import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,17,0))
w1=cq.Workplane('XY',origin=(0,0,10))
r=w0.sketch().arc((-100,-72),(-85,-95),(-60,-100)).segment((65,-100)).segment((94,-86)).segment((100,-70)).segment((100,-17)).segment((50,-1)).arc((48,-8),(44,-14)).segment((50,-1)).segment((48,-1)).segment((48,1)).segment((50,1)).segment((50,11)).segment((44,11)).arc((48,7),(50,1)).segment((44,1)).segment((26,26)).segment((100,54)).segment((100,74)).segment((99,74)).arc((85,95),(65,100)).segment((-60,100)).segment((-94,87)).segment((-100,72)).segment((-100,1)).segment((-50,1)).arc((-48,7),(-44,11)).segment((-50,-1)).segment((-48,-1)).segment((-48,-11)).segment((-44,-11)).arc((-48,-17),(-50,-24)).segment((-50,-54)).segment((-100,-72)).assemble().reset().face(w0.sketch().arc((-50,-54),(-24,-68),(4,-68)).segment((4,-43)).segment((23,-43)).arc((34,-21),(50,-1)).segment((44,-1)).arc((48,7),(50,11)).segment((50,54)).segment((53,54)).arc((24,68),(-4,68)).segment((-4,43)).segment((4,43)).segment((4,35)).arc((-24,28),(-50,11)).segment((-50,-1)).segment((-44,-1)).arc((-48,-9),(-50,-17)).close().assemble(),mode='s').finalize().extrude(-34).union(w1.workplane(offset=-110/2).moveTo(53,0).cylinder(110,16))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0050_00506931.step')
