import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-80))
w1=cq.Workplane('XY',origin=(0,0,-74))
r=w0.sketch().segment((-17,-21),(5,-30)).segment((10,-18)).arc((31,-15),(23,5)).segment((30,19)).segment((1,30)).close().assemble().push([(10,-1)]).circle(18,mode='s').finalize().extrude(-20).union(w0.sketch().arc((-34,6),(-14,19),(-1,1)).arc((-14,20),(-34,6)).assemble().reset().face(w0.sketch().arc((-33,-7),(-29,-14),(-22,-19)).arc((-14,-20),(-7,-18)).arc((-1,-14),(4,-7)).arc((-14,-16),(-33,-7)).assemble()).finalize().extrude(180)).union(w1.sketch().arc((-34,6),(-14,-21),(4,7)).arc((-14,1),(-34,6)).assemble().finalize().extrude(174))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0083_00838017.step')
