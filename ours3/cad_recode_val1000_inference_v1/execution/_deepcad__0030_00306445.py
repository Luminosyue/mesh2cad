import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,75,0))
w1=cq.Workplane('YZ',origin=(33,0,0))
r=w0.sketch().segment((-31,-93),(-28,-93)).segment((-5,-19)).segment((-31,-19)).close().assemble().reset().face(w0.sketch().segment((-31,-16),(-2,10)).segment((11,38)).segment((-31,55)).close().assemble()).reset().face(w0.sketch().segment((-31,60),(-28,60)).segment((-31,90)).close().assemble()).reset().face(w0.sketch().segment((-11,60),(25,60)).segment((25,93)).segment((22,93)).close().assemble()).finalize().extrude(-150).union(w0.sketch().segment((-30,-83),(-29,-83)).segment((-29,-93)).segment((-27,-93)).segment((-27,-83)).segment((-23,-83)).segment((-23,-75)).segment((-27,-75)).segment((-27,-65)).segment((-29,-65)).segment((-29,-75)).segment((-30,-75)).close().assemble().finalize().extrude(-148)).union(w1.sketch().segment((-75,-30),(-10,-30)).arc((22,-31),(48,-10)).arc((46,-21),(40,-30)).segment((75,-30)).segment((75,13)).arc((65,23),(54,18)).arc((53,19),(52,20)).arc((53,19),(54,17)).arc((56,17),(57,16)).arc((56,17),(54,18)).arc((53,19),(52,20)).arc((22,19),(-10,7)).segment((-75,7)).close().assemble().finalize().extrude(67))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00306445.step')
