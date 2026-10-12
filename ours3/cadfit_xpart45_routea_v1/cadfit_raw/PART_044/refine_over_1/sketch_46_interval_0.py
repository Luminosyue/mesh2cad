import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.90929), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03479, 0.71098)
loop_1 = loop_1.lineTo(-0.04361, 0.68603)
loop_1 = loop_1.threePointArc((-0.04736, 0.67559), (-0.05069, 0.66565))
loop_1 = loop_1.lineTo(-0.05525, 0.65112)
loop_1 = loop_1.threePointArc((-0.06201, 0.62814), (-0.06784, 0.60605))
loop_1 = loop_1.threePointArc((-0.06684, 0.58989), (-0.06399, 0.57481))
loop_1 = loop_1.threePointArc((-0.0619, 0.56094), (-0.06095, 0.55626))
loop_1 = loop_1.threePointArc((-0.05866, 0.54289), (-0.05746, 0.52899))
loop_1 = loop_1.lineTo(-0.05698, 0.49906)
loop_1 = loop_1.lineTo(-0.13915, 0.55417)
loop_1 = loop_1.lineTo(-0.03479, 0.71097)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.57)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_46_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_46_interval_0.stl')