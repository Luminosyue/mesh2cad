import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('ZX',origin=(0,48,0))
r=w0.sketch().segment((-4,-49),(4,-49)).segment((4,-5)).arc((0,-3),(4,-1)).segment((4,49)).segment((-4,49)).close().assemble().finalize().extrude(1).union(w1.sketch().segment((-95,-4),(-23,-4)).segment((-23,-3)).segment((10,-3)).segment((10,-4)).segment((100,-4)).segment((100,4)).segment((-95,4)).close().assemble().finalize().extrude(2))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0016_00161546.step')
