import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01219, 0.02256)
loop_1 = loop_1.lineTo(-0.00178, 0.01774)
loop_1 = loop_1.lineTo(0.00455, -0.00162)
loop_1 = loop_1.lineTo(0.00184, -0.0153)
loop_1 = loop_1.lineTo(-0.00421, -0.0294)
loop_1 = loop_1.lineTo(-0.01564, -0.04376)
loop_1 = loop_1.lineTo(-0.02925, -0.04678)
loop_1 = loop_1.lineTo(-0.04292, -0.03416)
loop_1 = loop_1.threePointArc((-0.04577, -0.02479), (-0.04734, -0.01759))
loop_1 = loop_1.threePointArc((-0.04818, -0.01078), (-0.04917, -0.00434))
loop_1 = loop_1.lineTo(-0.04907, 0.00914)
loop_1 = loop_1.lineTo(-0.02881, 0.02317)
loop_1 = loop_1.threePointArc((-0.02206, 0.0232), (-0.01557, 0.02325))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.73)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/sketch_27_interval_0.stl')