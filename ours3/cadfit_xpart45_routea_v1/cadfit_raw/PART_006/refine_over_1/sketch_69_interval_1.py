import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.38059, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.85418, 0.53609)
loop_1 = loop_1.lineTo(-0.80485, -0.00143)
loop_1 = loop_1.lineTo(-0.84047, 0.04553)
loop_1 = loop_1.threePointArc((-0.85037, 0.06861), (-0.85947, 0.09274))
loop_1 = loop_1.lineTo(-0.86711, 0.11304)
loop_1 = loop_1.lineTo(-0.87478, 0.14946)
loop_1 = loop_1.threePointArc((-0.87457, 0.20383), (-0.87358, 0.26007))
loop_1 = loop_1.lineTo(-0.87536, 0.36299)
loop_1 = loop_1.threePointArc((-0.87506, 0.39214), (-0.87549, 0.41977))
loop_1 = loop_1.threePointArc((-0.8763, 0.44147), (-0.87598, 0.46371))
loop_1 = loop_1.threePointArc((-0.87268, 0.48875), (-0.87046, 0.51253))
loop_1 = loop_1.lineTo(-0.85438, 0.53575)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_69_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_69_interval_1.stl')