import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-26))
r=w0.sketch().segment((64,-68),(95,-68)).segment((95,-66)).segment((100,-66)).segment((100,-35)).segment((95,-35)).segment((95,-30)).segment((87,-30)).arc((79,-25),(71,-30)).segment((64,-30)).close().assemble().finalize().extrude(12).union(w0.sketch().push([(-64,31)]).circle(36).circle(24,mode='s').finalize().extrude(35)).union(w0.workplane(offset=52/2).moveTo(-64,31).cylinder(52,36))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0023_00237164.step')
