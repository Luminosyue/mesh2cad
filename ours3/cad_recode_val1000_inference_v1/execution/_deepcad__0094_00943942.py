import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-1,0))
r=w0.sketch().segment((-100,-10),(-7,-10)).arc((0,-10),(7,-8)).segment((98,-10)).segment((100,8)).segment((10,10)).arc((0,10),(-7,8)).segment((-98,10)).close().assemble().finalize().extrude(2)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0094_00943942.step')
