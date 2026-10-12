import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-100,-3),(-91,-3)).segment((-91,-7)).segment((91,-7)).segment((91,-3)).segment((97,-3)).segment((97,3)).segment((91,3)).segment((91,7)).segment((-91,7)).segment((-91,3)).segment((-100,3)).close().assemble().finalize().extrude(-2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0037_00372378.step')
