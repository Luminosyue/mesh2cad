import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,3))
r=w0.sketch().segment((-100,-7),(-26,-7)).arc((-25,-2),(-24,2)).segment((-67,2)).segment((-67,7)).segment((-100,7)).close().assemble().reset().face(w0.sketch().segment((-19,7),(-15,7)).arc((-17,8),(-19,7)).assemble()).reset().face(w0.sketch().segment((-15,-7),(49,-7)).arc((50,-3),(51,-7)).segment((100,-7)).segment((100,7)).segment((74,7)).arc((72,4),(70,7)).segment((-5,7)).arc((-6,3),(-8,1)).segment((-8,0)).segment((-9,0)).arc((-12,-3),(-15,-7)).assemble()).finalize().extrude(-6)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0060_00601452.step')
