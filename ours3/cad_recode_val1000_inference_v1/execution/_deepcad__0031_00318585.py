import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-96,0))
r=w0.sketch().segment((-67,-67),(-4,-67)).segment((67,-2)).segment((-4,67)).segment((-67,67)).close().assemble().finalize().extrude(200).union(w1.sketch().segment((53,12),(53,14)).arc((50,10),(55,12)).close().assemble().finalize().extrude(187))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0031_00318585.step')
