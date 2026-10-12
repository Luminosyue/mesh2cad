import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,5))
r=w0.sketch().segment((-100,-38),(-52,-38)).arc((-56,-32),(-57,-25)).segment((-78,-23)).segment((-76,-10)).segment((-55,-12)).arc((-47,-15),(-40,-18)).segment((-29,-19)).segment((-30,-32)).arc((-29,-35),(-29,-38)).segment((8,-38)).arc((10,-32),(14,-27)).segment((14,-6)).segment((44,-16)).segment((44,-38)).segment((100,-38)).segment((100,38)).segment((23,38)).segment((23,30)).segment((-6,38)).segment((-10,25)).segment((10,20)).arc((-1,10),(-10,0)).segment((-10,-12)).segment((-31,-10)).arc((-39,14),(-33,38)).segment((-100,38)).close().assemble().push([(61,10)]).circle(14,mode='s').finalize().extrude(-10)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0068_00681849.step')
