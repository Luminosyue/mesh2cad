import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,1))
r=w0.sketch().segment((-100,-10),(-97,-10)).segment((-97,-20)).segment((-76,-20)).segment((-76,-23)).segment((-52,-23)).segment((-52,-20)).segment((-50,-20)).segment((-50,-10)).segment((-47,-10)).segment((-47,-9)).segment((-29,-9)).segment((-29,-23)).segment((24,-23)).segment((24,-17)).segment((100,-19)).segment((100,19)).segment((24,21)).segment((24,23)).segment((-29,23)).segment((-29,18)).segment((-52,18)).segment((-52,23)).segment((-97,23)).segment((-97,12)).segment((-100,12)).close().assemble().push([(62,4)]).circle(13,mode='s').finalize().extrude(-3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0052_00525982.step')
