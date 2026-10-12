import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.55205, -0.81417, -0.01566), normal=(0.56402, 0.82576, -0.00038), xDir=(0.82576, -0.56402, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.20244, -0.08706)
loop_1 = loop_1.lineTo(-0.22165, 0.03483)
loop_1 = loop_1.lineTo(-0.22274, -0.0963)
loop_1 = loop_1.lineTo(-0.20358, -0.08904)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_24_interval_0.stl')