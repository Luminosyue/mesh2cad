import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,100))
w1=cq.Workplane('XY',origin=(0,0,17))
r=w0.sketch().arc((-29,12),(-30,-8),(-18,-25)).close().assemble().reset().face(w0.sketch().segment((-25,19),(24,20)).arc((0,31),(-25,19)).assemble()).reset().face(w0.sketch().arc((-14,-28),(10,-30),(29,-12)).close().assemble()).reset().face(w0.sketch().segment((24,20),(30,-8)).arc((30,8),(24,20)).assemble()).finalize().extrude(-193).union(w0.sketch().arc((-18,0),(17,-6),(-17,5)).arc((-17,3),(-18,0)).assemble().finalize().extrude(-193)).union(w1.sketch().push([(0,-1)]).circle(31).circle(18,mode='s').finalize().extrude(-110))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0033_00339606.step')
