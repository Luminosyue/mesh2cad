import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,10))
w1=cq.Workplane('YZ',origin=(-11,0,0))
r=w0.sketch().arc((-100,12),(-97,3),(-94,-6)).close().assemble().reset().face(w0.sketch().segment((-99,14),(-44,27)).segment((-35,-10)).segment((-87,-32)).arc((-62,-45),(-35,-41)).arc((-25,-33),(-15,-25)).segment((-15,-21)).segment((-12,-21)).arc((-11,-20),(-10,-19)).segment((-15,-19)).segment((-15,-17)).segment((-17,-17)).arc((-17,20),(-47,45)).arc((-71,43),(-90,30)).arc((-95,23),(-99,14)).assemble()).finalize().extrude(-20).union(w0.sketch().segment((-1,-32),(96,-31)).segment((96,-24)).segment((100,-24)).segment((100,-10)).segment((96,-10)).segment((96,-1)).segment((77,-1)).segment((77,0)).segment((41,0)).segment((41,-1)).segment((28,-1)).segment((28,-6)).segment((20,-6)).segment((20,0)).segment((1,0)).segment((1,-10)).segment((-1,-10)).close().assemble().finalize().extrude(-10)).union(w1.sketch().arc((17,-8),(23,-5),(22,1)).arc((20,-4),(17,-8)).assemble().finalize().extrude(42))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0064_00649289.step')
