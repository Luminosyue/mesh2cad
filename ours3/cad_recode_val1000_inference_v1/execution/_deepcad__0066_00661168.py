import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,20,0))
w1=cq.Workplane('ZX',origin=(0,16,0))
r=w0.sketch().segment((-100,-37),(-75,-42)).segment((-75,-41)).segment((-73,-41)).segment((-73,-42)).segment((-37,-48)).segment((-37,-46)).segment((37,-5)).segment((37,-4)).segment((39,-4)).segment((39,-5)).segment((97,26)).segment((95,30)).segment((39,1)).segment((39,0)).segment((37,0)).segment((37,1)).segment((-12,12)).segment((-23,86)).segment((-24,86)).segment((-35,19)).segment((-33,19)).segment((-33,17)).segment((-36,17)).segment((-36,19)).segment((-37,19)).segment((-37,18)).segment((-73,-22)).segment((-73,-21)).segment((-75,-21)).segment((-75,-22)).segment((-96,-35)).segment((-96,-36)).segment((-97,-36)).segment((-97,-35)).close().assemble().finalize().extrude(-40).union(w0.sketch().segment((-18,-51),(38,-86)).segment((23,-62)).segment((10,-45)).arc((-5,-54),(-18,-51)).assemble().finalize().extrude(-35)).union(w1.sketch().arc((77,16),(84,20),(92,23)).arc((84,24),(77,24)).close().assemble().finalize().extrude(-34))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0066_00661168.step')
