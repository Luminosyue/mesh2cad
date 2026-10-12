import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.01473, -0.3497, 0.072), normal=(0.56482, 0.82522, -3e-05), xDir=(0.82522, -0.56482, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.19755, 0.56076)
loop_1 = loop_1.lineTo(-0.20987, 0.5604)
loop_1 = loop_1.lineTo(-0.21786, 0.53773)
loop_1 = loop_1.threePointArc((-0.21841, 0.5292), (-0.2187, 0.52099))
loop_1 = loop_1.lineTo(-0.21895, 0.50634)
loop_1 = loop_1.threePointArc((-0.2191, 0.48824), (-0.2195, 0.47152))
loop_1 = loop_1.lineTo(-0.2195, 0.44112)
loop_1 = loop_1.threePointArc((-0.22008, 0.42475), (-0.22007, 0.41175))
loop_1 = loop_1.lineTo(-0.21997, 0.39819)
loop_1 = loop_1.lineTo(-0.21936, 0.37127)
loop_1 = loop_1.lineTo(-0.2183, 0.35921)
loop_1 = loop_1.lineTo(-0.1162, 0.53103)
loop_1 = loop_1.lineTo(-0.12926, 0.53531)
loop_1 = loop_1.threePointArc((-0.14663, 0.54106), (-0.15642, 0.54455))
loop_1 = loop_1.lineTo(-0.19755, 0.56076)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_24_interval_0.stl')