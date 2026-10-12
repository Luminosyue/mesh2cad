import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-13,0))
r=w0.sketch().segment((-13,-98),(-10,-98)).segment((-10,-100)).segment((13,-100)).segment((13,100)).segment((-10,100)).segment((-10,98)).segment((-13,98)).close().assemble().push([(-11,0)]).circle(2,mode='s').push([(11,0)]).rect(4,18,mode='s').finalize().extrude(26)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0023_00237679.step')
