import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,6,0))
r=w0.sketch().segment((-100,1),(-98,1)).arc((-88,-45),(-56,-80)).segment((-56,-82)).segment((-54,-82)).arc((0,-99),(54,-82)).segment((56,-82)).segment((56,-80)).arc((88,-45),(98,1)).segment((100,1)).segment((100,3)).segment((98,3)).arc((88,45),(56,80)).segment((56,82)).segment((54,82)).arc((0,99),(-54,82)).segment((-56,82)).segment((-56,80)).arc((-88,45),(-98,3)).segment((-100,3)).close().assemble().circle(96,mode='s').finalize().extrude(-12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0017_00175604.step')
