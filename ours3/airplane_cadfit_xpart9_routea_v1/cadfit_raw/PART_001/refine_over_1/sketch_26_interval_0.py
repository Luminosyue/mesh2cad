import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.37469, -0.02439, 0.03338), normal=(0.04748, 0.16366, 0.98537), xDir=(0.0, 0.98649, -0.16384))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33431, 0.00946)
loop_1 = loop_1.lineTo(-0.27916, 0.22964)
loop_1 = loop_1.lineTo(-0.22924, 0.40692)
loop_1 = loop_1.lineTo(-0.18111, 0.55841)
loop_1 = loop_1.lineTo(-0.38389, 0.56643)
loop_1 = loop_1.lineTo(-0.38392, 0.54542)
loop_1 = loop_1.lineTo(-0.38021, 0.44563)
loop_1 = loop_1.lineTo(-0.37623, 0.37301)
loop_1 = loop_1.threePointArc((-0.36613, 0.24772), (-0.35548, 0.13556))
loop_1 = loop_1.threePointArc((-0.34829, 0.07376), (-0.34113, 0.02061))
loop_1 = loop_1.lineTo(-0.3372, 0.0085)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_26_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_26_interval_0.stl')