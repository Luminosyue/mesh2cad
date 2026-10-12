import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,50,0))
r=w0.sketch().segment((-100,-100),(100,-100)).segment((100,97)).segment((78,97)).segment((78,100)).segment((-100,100)).close().assemble().push([(20,30)]).circle(18,mode='s').finalize().extrude(-100)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0094_00941713.step')
