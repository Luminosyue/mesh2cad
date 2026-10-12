import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.54077, -0.79766, -0.01566), normal=(0.56402, 0.82576, -0.00038), xDir=(0.82576, -0.56402, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28334, 0.5011)
loop_1 = loop_1.lineTo(-0.29603, 0.48183)
loop_1 = loop_1.lineTo(-0.31522, 0.44911)
loop_1 = loop_1.lineTo(-0.31977, 0.43665)
loop_1 = loop_1.lineTo(-0.32752, 0.41346)
loop_1 = loop_1.lineTo(-0.32763, 0.50383)
loop_1 = loop_1.lineTo(-0.28043, 0.50383)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_0_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_0_interval_0.stl')