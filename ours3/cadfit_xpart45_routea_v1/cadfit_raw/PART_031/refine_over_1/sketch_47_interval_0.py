import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.69906, -0.67731, 0.08), normal=(-0.78886, 0.61456, -0.00322), xDir=(0.61457, 0.78886, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34399, 0.60571)
loop_1 = loop_1.lineTo(-0.35219, 0.58923)
loop_1 = loop_1.lineTo(-0.35918, 0.56823)
loop_1 = loop_1.lineTo(-0.36243, 0.53347)
loop_1 = loop_1.threePointArc((-0.36351, 0.52517), (-0.3644, 0.51843))
loop_1 = loop_1.lineTo(-0.36357, 0.48559)
loop_1 = loop_1.threePointArc((-0.36469, 0.47742), (-0.36555, 0.47116))
loop_1 = loop_1.lineTo(-0.36468, 0.62311)
loop_1 = loop_1.lineTo(-0.33005, 0.62311)
loop_1 = loop_1.lineTo(-0.34323, 0.60725)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_031/refine_over_1/sketch_47_interval_0.stl')