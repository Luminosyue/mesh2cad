import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.86162, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.7157, 0.19447)
loop_1 = loop_1.threePointArc((-0.70425, 0.19838), (-0.69172, 0.19965))
loop_1 = loop_1.threePointArc((-0.63239, 0.20286), (-0.57115, 0.20302))
loop_1 = loop_1.threePointArc((-0.5161, 0.20371), (-0.4594, 0.20288))
loop_1 = loop_1.lineTo(-0.34781, 0.20331)
loop_1 = loop_1.lineTo(-0.09264, 0.20398)
loop_1 = loop_1.lineTo(0.13255, 0.20475)
loop_1 = loop_1.lineTo(0.18338, 0.20593)
loop_1 = loop_1.threePointArc((-0.07432, 0.20554), (-0.34286, 0.20563))
loop_1 = loop_1.lineTo(-0.71573, 0.20415)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.69)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_49_interval_0.stl')