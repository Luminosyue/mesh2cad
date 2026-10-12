import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.083, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.57044, -0.92274)
loop_1 = loop_1.lineTo(-0.57197, -0.89826)
loop_1 = loop_1.lineTo(-0.57358, -0.87039)
loop_1 = loop_1.lineTo(-0.58178, -0.83681)
loop_1 = loop_1.lineTo(-0.61049, -0.82145)
loop_1 = loop_1.lineTo(-0.62666, -0.80449)
loop_1 = loop_1.lineTo(-0.66518, -0.78792)
loop_1 = loop_1.lineTo(-0.5705, -0.92265)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.22)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_37_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_044/refine_over_1/sketch_37_interval_0.stl')