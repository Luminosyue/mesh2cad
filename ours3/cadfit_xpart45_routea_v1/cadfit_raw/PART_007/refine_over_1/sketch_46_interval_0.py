import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.98961, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.64947, -0.00289)
loop_1 = loop_1.lineTo(-0.64887, -0.32)
loop_1 = loop_1.lineTo(-0.56143, -0.31969)
loop_1 = loop_1.lineTo(-0.56161, -0.3073)
loop_1 = loop_1.threePointArc((-0.57099, -0.29353), (-0.57949, -0.27876))
loop_1 = loop_1.lineTo(-0.59271, -0.25468)
loop_1 = loop_1.threePointArc((-0.60114, -0.23531), (-0.60958, -0.21533))
loop_1 = loop_1.threePointArc((-0.61324, -0.19908), (-0.61672, -0.18242))
loop_1 = loop_1.threePointArc((-0.61823, -0.17581), (-0.61888, -0.1691))
loop_1 = loop_1.lineTo(-0.62257, -0.13323)
loop_1 = loop_1.lineTo(-0.62724, -0.10566)
loop_1 = loop_1.threePointArc((-0.63222, -0.08212), (-0.6375, -0.05993))
loop_1 = loop_1.lineTo(-0.64575, -0.02316)
loop_1 = loop_1.threePointArc((-0.63772, -0.05547), (-0.63018, -0.08958))
loop_1 = loop_1.lineTo(-0.64906, -0.00386)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_46_interval_0.stl')