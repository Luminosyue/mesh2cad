import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.71759, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.70471, -0.27098)
loop_1 = loop_1.lineTo(0.83649, -0.28914)
loop_1 = loop_1.lineTo(0.81846, -0.30146)
loop_1 = loop_1.threePointArc((0.78136, -0.31282), (0.74219, -0.31602))
loop_1 = loop_1.threePointArc((0.63352, -0.31796), (0.5214, -0.31795))
loop_1 = loop_1.threePointArc((0.44808, -0.31826), (0.37872, -0.31992))
loop_1 = loop_1.lineTo(0.11717, -0.3203)
loop_1 = loop_1.threePointArc((0.03093, -0.31982), (-0.05776, -0.31722))
loop_1 = loop_1.lineTo(-0.20883, -0.31516)
loop_1 = loop_1.threePointArc((-0.31605, -0.31425), (-0.42662, -0.31159))
loop_1 = loop_1.threePointArc((-0.52663, -0.30899), (-0.62963, -0.3039))
loop_1 = loop_1.lineTo(-0.65052, -0.29604)
loop_1 = loop_1.lineTo(-0.67524, -0.29346)
loop_1 = loop_1.lineTo(-0.69532, -0.28405)
loop_1 = loop_1.lineTo(-0.70408, -0.27185)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.42)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_034/refine_under_1/sketch_49_interval_0.stl')