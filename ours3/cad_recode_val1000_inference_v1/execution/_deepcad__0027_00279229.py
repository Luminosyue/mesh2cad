import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-6,0))
r=w0.sketch().segment((-15,-100),(12,-100)).segment((12,-84)).segment((15,-84)).segment((15,-42)).arc((5,-10),(15,33)).segment((15,100)).segment((-15,100)).segment((-15,42)).arc((-5,10),(-15,-33)).close().assemble().push([(-8,-93)]).circle(4,mode='s').finalize().extrude(12)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0027_00279229.step')
