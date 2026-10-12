import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-2,0))
r=w0.sketch().segment((-100,20),(-93,-19)).segment((-67,-15)).segment((-67,-20)).segment((36,-20)).segment((36,-17)).segment((53,-17)).segment((53,-20)).segment((94,-20)).segment((94,-17)).segment((100,-17)).segment((100,14)).segment((94,14)).segment((94,20)).segment((33,20)).segment((33,14)).segment((17,14)).segment((17,20)).segment((-34,20)).segment((-34,17)).segment((-37,17)).segment((-37,20)).close().assemble().reset().face(w0.sketch().segment((-31,-17),(-29,-17)).segment((-29,-16)).segment((-28,-16)).segment((-28,-17)).segment((-26,-17)).segment((-26,-18)).segment((-28,-18)).segment((-28,-19)).segment((-29,-19)).segment((-29,-18)).segment((-31,-18)).close().assemble(),mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0019_00195132.step')
