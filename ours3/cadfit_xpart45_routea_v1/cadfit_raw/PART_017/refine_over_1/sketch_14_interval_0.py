import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.58687, -0.04406, 0.50806), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.4282, -0.96687)
loop_1 = loop_1.lineTo(-0.48044, -0.96687)
loop_1 = loop_1.lineTo(-0.4803, -0.70516)
loop_1 = loop_1.lineTo(-0.48004, -0.71789)
loop_1 = loop_1.lineTo(-0.47838, -0.75306)
loop_1 = loop_1.lineTo(-0.47734, -0.76316)
loop_1 = loop_1.lineTo(-0.47552, -0.7917)
loop_1 = loop_1.threePointArc((-0.47103, -0.81673), (-0.46706, -0.83736))
loop_1 = loop_1.threePointArc((-0.46196, -0.85859), (-0.45768, -0.876))
loop_1 = loop_1.threePointArc((-0.45174, -0.89638), (-0.44648, -0.91464))
loop_1 = loop_1.lineTo(-0.43189, -0.95709)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.99)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_14_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_14_interval_0.stl')