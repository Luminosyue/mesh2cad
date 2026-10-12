import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,67))
w1=cq.Workplane('ZX',origin=(0,33,0))
r=w0.sketch().segment((-100,-75),(-76,-75)).arc((-88,-67),(-100,-57)).close().assemble().reset().face(w0.sketch().arc((-100,-12),(-88,-3),(-76,5)).segment((-67,5)).segment((-67,75)).segment((-100,75)).close().assemble()).reset().face(w0.sketch().segment((67,-75),(100,-75)).segment((100,-57)).arc((88,-67),(76,-75)).segment((100,-75)).segment((100,75)).segment((67,75)).arc((68,73),(68,71)).segment((67,71)).segment((67,-25)).segment((100,-25)).segment((100,-37)).segment((67,-37)).close().assemble()).finalize().extrude(-134).union(w1.sketch().arc((-61,17),(-52,10),(-42,5)).arc((-3,-47),(59,-24)).arc((26,3),(59,30)).arc((1,14),(-49,43)).arc((-55,29),(-61,17)).assemble().finalize().extrude(-33))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0082_00826981.step')
