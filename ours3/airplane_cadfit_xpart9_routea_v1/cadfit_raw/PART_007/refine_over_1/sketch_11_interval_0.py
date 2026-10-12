import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.25021, 0.61919, 0.05517), normal=(-0.01834, -0.26424, -0.96428), xDir=(0.0, -0.96445, 0.26428))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28812, 0.75722)
loop_1 = loop_1.threePointArc((-0.28591, 0.77587), (-0.27916, 0.79422))
loop_1 = loop_1.lineTo(-0.26783, 0.81967)
loop_1 = loop_1.lineTo(-0.25356, 0.84845)
loop_1 = loop_1.lineTo(-0.24634, 0.86164)
loop_1 = loop_1.lineTo(-0.2161, 0.40982)
loop_1 = loop_1.lineTo(-0.22459, 0.45154)
loop_1 = loop_1.lineTo(-0.23118, 0.47438)
loop_1 = loop_1.threePointArc((-0.23363, 0.48143), (-0.23627, 0.48809))
loop_1 = loop_1.lineTo(-0.24952, 0.54576)
loop_1 = loop_1.lineTo(-0.25936, 0.59354)
loop_1 = loop_1.lineTo(-0.26845, 0.64231)
loop_1 = loop_1.lineTo(-0.27541, 0.67169)
loop_1 = loop_1.lineTo(-0.28107, 0.70141)
loop_1 = loop_1.threePointArc((-0.28365, 0.71817), (-0.28539, 0.73116))
loop_1 = loop_1.lineTo(-0.28767, 0.75288)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.19)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_11_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_11_interval_0.stl')