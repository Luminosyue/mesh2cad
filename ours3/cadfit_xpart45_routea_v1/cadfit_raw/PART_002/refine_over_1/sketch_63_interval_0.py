import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.25412, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29281, 0.77)
loop_1 = loop_1.lineTo(-0.30355, 0.75085)
loop_1 = loop_1.threePointArc((-0.30773, 0.74032), (-0.31219, 0.72958))
loop_1 = loop_1.threePointArc((-0.3156, 0.72136), (-0.31852, 0.71349))
loop_1 = loop_1.threePointArc((-0.3246, 0.69039), (-0.33017, 0.66831))
loop_1 = loop_1.threePointArc((-0.33383, 0.65174), (-0.33706, 0.63594))
loop_1 = loop_1.lineTo(-0.34346, 0.60115)
loop_1 = loop_1.threePointArc((-0.34797, 0.58182), (-0.35189, 0.56334))
loop_1 = loop_1.lineTo(-0.35188, 0.77)
loop_1 = loop_1.lineTo(-0.29297, 0.77)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_63_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_63_interval_0.stl')