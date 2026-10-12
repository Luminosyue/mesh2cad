import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-24,0))
w1=cq.Workplane('ZX',origin=(0,-45,0))
r=w0.sketch().segment((-29,-38),(-22,-42)).arc((-14,-46),(-5,-47)).segment((2,-51)).segment((5,-47)).arc((35,-29),(36,7)).segment((39,11)).segment((32,15)).arc((24,20),(15,23)).segment((7,27)).segment((4,23)).arc((-26,5),(-27,-31)).close().assemble().push([(4,-12)]).circle(26,mode='s').finalize().extrude(-76).union(w0.sketch().segment((-61,-34),(-7,-62)).segment((61,12)).segment((23,42)).segment((23,-19)).segment((5,-19)).segment((5,57)).segment((-6,62)).segment((-17,44)).arc((-14,40),(-11,36)).segment((-11,37)).segment((-10,36)).arc((-11,35),(-11,34)).segment((-16,34)).arc((-25,3),(-50,-19)).segment((-45,-19)).close().assemble().finalize().extrude(19)).union(w0.sketch().segment((-47,6),(-38,6)).arc((4,38),(47,6)).segment((47,17)).segment((43,17)).arc((4,48),(-35,17)).segment((-47,17)).close().assemble().finalize().extrude(118)).union(w1.sketch().arc((-47,-8),(-38,-3),(-38,7)).arc((-39,10),(-40,12)).arc((-43,14),(-45,17)).arc((-46,12),(-47,6)).close().assemble().finalize().extrude(-52))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__128996_b005b1f9_0000.step')
