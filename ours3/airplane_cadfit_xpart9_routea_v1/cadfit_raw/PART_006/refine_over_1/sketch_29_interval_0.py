import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.90949, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.30463, 0.05351)
loop_1 = loop_1.threePointArc((0.32902, 0.05024), (0.35249, 0.04755))
loop_1 = loop_1.threePointArc((0.38124, 0.04358), (0.40858, 0.04046))
loop_1 = loop_1.threePointArc((0.42787, 0.03765), (0.44614, 0.03564))
loop_1 = loop_1.lineTo(0.5206, 0.02487)
loop_1 = loop_1.threePointArc((0.54083, 0.02106), (0.56143, 0.01649))
loop_1 = loop_1.threePointArc((0.56706, 0.01541), (0.57228, 0.01335))
loop_1 = loop_1.lineTo(0.58753, 0.00791)
loop_1 = loop_1.threePointArc((0.60185, -0.00211), (0.60673, -0.005))
loop_1 = loop_1.threePointArc((0.61589, -0.01362), (0.62451, -0.02297))
loop_1 = loop_1.threePointArc((0.63806, -0.03778), (0.65111, -0.05366))
loop_1 = loop_1.lineTo(0.6506, 0.06508)
loop_1 = loop_1.lineTo(0.2181, 0.06444)
loop_1 = loop_1.threePointArc((0.23767, 0.06206), (0.25764, 0.0591))
loop_1 = loop_1.threePointArc((0.28068, 0.05653), (0.30427, 0.05338))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.77)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_29_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_29_interval_0.stl')