import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-19,0))
r=w0.sketch().segment((-100,-19),(100,-19)).segment((100,19)).segment((-100,19)).segment((-100,12)).segment((-98,12)).segment((-98,9)).segment((-100,9)).close().assemble().push([(-62,-12)]).circle(7,mode='s').push([(0,0)]).rect(4,38,mode='s').finalize().extrude(38)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0042_00422949.step')
