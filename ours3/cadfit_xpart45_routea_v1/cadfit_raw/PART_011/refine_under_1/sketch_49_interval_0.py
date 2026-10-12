import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.71298, -0.49236, -0.01805), normal=(-0.86978, 0.49324, 0.014), xDir=(0.49329, 0.86986, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28067, 0.27132)
loop_1 = loop_1.lineTo(-0.28432, 0.12331)
loop_1 = loop_1.lineTo(-0.29302, -0.22878)
loop_1 = loop_1.lineTo(-0.30745, -0.22629)
loop_1 = loop_1.lineTo(-0.33142, -0.21775)
loop_1 = loop_1.lineTo(-0.34977, -0.21652)
loop_1 = loop_1.lineTo(-0.34797, -0.16887)
loop_1 = loop_1.lineTo(-0.33132, -0.04698)
loop_1 = loop_1.lineTo(-0.34685, -0.13917)
loop_1 = loop_1.lineTo(-0.34571, -0.10891)
loop_1 = loop_1.lineTo(-0.31611, 0.26456)
loop_1 = loop_1.lineTo(-0.30469, 0.26784)
loop_1 = loop_1.lineTo(-0.29458, 0.26981)
loop_1 = loop_1.lineTo(-0.28067, 0.27132)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.17)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_011/refine_under_1/sketch_49_interval_0.stl')