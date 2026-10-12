import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.50895, -0.81315, 0.04103), normal=(-0.61375, 0.7895, 0.00198), xDir=(0.7895, 0.61375, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.0052, 0.24689)
loop_1 = loop_1.lineTo(0.03673, 0.24529)
loop_1 = loop_1.lineTo(0.04825, 0.24412)
loop_1 = loop_1.lineTo(0.05919, 0.24159)
loop_1 = loop_1.lineTo(0.10674, 0.22596)
loop_1 = loop_1.lineTo(0.09422, 0.22418)
loop_1 = loop_1.lineTo(0.07431, 0.22858)
loop_1 = loop_1.lineTo(0.06324, 0.2267)
loop_1 = loop_1.lineTo(0.04449, 0.23044)
loop_1 = loop_1.lineTo(0.0306, 0.23692)
loop_1 = loop_1.lineTo(0.01516, 0.23685)
loop_1 = loop_1.lineTo(0.00064, 0.2305)
loop_1 = loop_1.lineTo(-0.00521, 0.24531)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_14_interval_0.stl')