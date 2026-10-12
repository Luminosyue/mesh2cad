import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.45927, 0.27402, -0.07227), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.01262, 0.39561)
loop_1 = loop_1.lineTo(-0.01165, 0.38004)
loop_1 = loop_1.lineTo(0.00727, 0.36802)
loop_1 = loop_1.lineTo(0.01846, 0.36661)
loop_1 = loop_1.lineTo(0.03741, 0.36615)
loop_1 = loop_1.lineTo(0.13638, 0.45999)
loop_1 = loop_1.lineTo(0.08315, 0.47726)
loop_1 = loop_1.lineTo(0.07357, 0.46705)
loop_1 = loop_1.lineTo(0.05361, 0.45855)
loop_1 = loop_1.lineTo(0.03414, 0.44989)
loop_1 = loop_1.lineTo(0.01531, 0.43863)
loop_1 = loop_1.lineTo(0.00354, 0.42607)
loop_1 = loop_1.lineTo(-0.00597, 0.41436)
loop_1 = loop_1.lineTo(-0.01327, 0.40058)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_5_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/refine_under_1/sketch_5_interval_0.stl')