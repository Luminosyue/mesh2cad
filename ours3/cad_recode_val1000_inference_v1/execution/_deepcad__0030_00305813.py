import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-90,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,100)).segment((-100,100)).segment((-100,40)).segment((-97,40)).segment((-97,36)).segment((-100,36)).close().assemble().push([(51,26)]).circle(37,mode='s').finalize().extrude(180)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0030_00305813.step')
