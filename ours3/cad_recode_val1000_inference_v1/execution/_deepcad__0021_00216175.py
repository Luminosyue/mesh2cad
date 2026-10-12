import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-98))
r=w0.sketch().segment((51,-5),(64,15)).arc((55,8),(51,-5)).assemble().reset().face(w0.sketch().arc((57,-7),(66,-15),(79,-6)).close().assemble()).reset().face(w0.sketch().segment((63,15),(79,3)).arc((70,13),(63,15)).assemble()).finalize().extrude(22).union(w0.sketch().push([(-65,0)]).circle(15).circle(9,mode='s').finalize().extrude(193)).union(w1.sketch().arc((-79,-7),(-65,-15),(-50,-7)).close().assemble().finalize().extrude(198))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0021_00216175.step')
