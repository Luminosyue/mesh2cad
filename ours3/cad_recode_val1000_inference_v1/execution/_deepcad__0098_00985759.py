import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-29))
w1=cq.Workplane('XY',origin=(0,0,-10))
r=w0.sketch().segment((-29,-46),(-2,-48)).segment((-2,-46)).arc((20,-47),(37,-36)).segment((33,-36)).segment((33,-13)).segment((63,-13)).segment((63,-30)).arc((68,-28),(72,-25)).segment((89,-19)).segment((88,-16)).segment((100,-3)).segment((90,7)).segment((90,4)).segment((68,4)).segment((68,17)).segment((80,17)).segment((54,34)).segment((46,20)).arc((37,29),(28,37)).segment((31,43)).segment((-12,50)).segment((-13,45)).segment((-29,46)).segment((-29,37)).arc((-100,-1),(-29,-40)).close().assemble().push([(12,0)]).circle(16,mode='s').finalize().extrude(20).union(w0.sketch().arc((-87,34),(-63,1),(-76,-37)).arc((-45,-51),(-13,-36)).arc((25,5),(-24,37)).arc((-56,51),(-87,34)).assemble().finalize().extrude(43)).union(w0.sketch().push([(2,1)]).circle(23).circle(16,mode='s').finalize().extrude(58)).union(w1.sketch().arc((-24,44),(-18,40),(-13,36)).segment((-13,45)).segment((-24,45)).close().assemble().finalize().extrude(8))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0098_00985759.step')
