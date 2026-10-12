import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.01908), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.02486, 0.59809)
loop_1 = loop_1.lineTo(-0.01276, 0.59687)
loop_1 = loop_1.lineTo(0.0078, 0.56123)
loop_1 = loop_1.lineTo(0.01133, 0.54163)
loop_1 = loop_1.lineTo(0.00627, 0.52353)
loop_1 = loop_1.lineTo(-0.00594, 0.5052)
loop_1 = loop_1.lineTo(-0.01424, 0.49465)
loop_1 = loop_1.lineTo(-0.02522, 0.59785)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_67_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_67_interval_0.stl')