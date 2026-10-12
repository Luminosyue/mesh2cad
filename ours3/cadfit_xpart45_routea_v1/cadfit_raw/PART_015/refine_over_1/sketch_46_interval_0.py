import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.32825), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.87714, -0.30145)
loop_1 = loop_1.lineTo(-0.72076, -0.52684)
loop_1 = loop_1.threePointArc((-0.72697, -0.51985), (-0.73308, -0.51203))
loop_1 = loop_1.threePointArc((-0.74961, -0.49142), (-0.76644, -0.4699))
loop_1 = loop_1.threePointArc((-0.77892, -0.4573), (-0.78581, -0.44749))
loop_1 = loop_1.lineTo(-0.81077, -0.41219)
loop_1 = loop_1.lineTo(-0.84034, -0.3665)
loop_1 = loop_1.threePointArc((-0.84795, -0.35566), (-0.85524, -0.34418))
loop_1 = loop_1.threePointArc((-0.86017, -0.33586), (-0.86494, -0.32719))
loop_1 = loop_1.threePointArc((-0.87105, -0.31495), (-0.87677, -0.30211))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.5)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_46_interval_0.stl')