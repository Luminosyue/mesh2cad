import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,45,0))
r=w0.sketch().arc((-58,46),(-99,-13),(-57,-76)).segment((-57,-82)).segment((-44,-82)).arc((0,-100),(44,-87)).segment((57,-87)).segment((57,-81)).arc((99,-13),(75,66)).arc((48,56),(47,88)).arc((3,100),(-40,91)).arc((-41,75),(-51,65)).arc((-55,55),(-58,46)).assemble().push([(0,-27)]).circle(29,mode='s').finalize().extrude(-90).union(w0.sketch().arc((-87,-49),(-11,37),(-10,-73)).arc((45,89),(-87,-49)).assemble().finalize().extrude(-70))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0079_00795734.step')
