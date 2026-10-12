import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25412, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34996, -0.60012)
loop_1 = loop_1.threePointArc((-0.34986, -0.59355), (-0.34996, -0.58724))
loop_1 = loop_1.lineTo(-0.35236, -0.65287)
loop_1 = loop_1.lineTo(-0.35192, -0.81)
loop_1 = loop_1.lineTo(-0.21852, -0.80956)
loop_1 = loop_1.lineTo(-0.23091, -0.80237)
loop_1 = loop_1.threePointArc((-0.25405, -0.76898), (-0.26835, -0.74616))
loop_1 = loop_1.lineTo(-0.27709, -0.73212)
loop_1 = loop_1.lineTo(-0.33864, -0.66746)
loop_1 = loop_1.lineTo(-0.34802, -0.65454)
loop_1 = loop_1.threePointArc((-0.34884, -0.6453), (-0.34942, -0.63589))
loop_1 = loop_1.lineTo(-0.35008, -0.6153)
loop_1 = loop_1.lineTo(-0.34972, -0.59521)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_61_interval_0.stl')