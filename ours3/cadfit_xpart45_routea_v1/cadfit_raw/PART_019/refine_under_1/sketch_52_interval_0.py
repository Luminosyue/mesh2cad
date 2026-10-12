import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.76958, -0.00272, 0.52538), normal=(-0.82856, 0.00156, -0.55989), xDir=(0.00188, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.09733, 0.3676)
loop_1 = loop_1.threePointArc((-0.05852, 0.36662), (-0.02126, 0.36638))
loop_1 = loop_1.lineTo(0.02604, 0.36538)
loop_1 = loop_1.threePointArc((0.12032, 0.36659), (0.21109, 0.36489))
loop_1 = loop_1.threePointArc((0.26279, 0.36554), (0.30908, 0.36548))
loop_1 = loop_1.lineTo(0.3501, 0.36319)
loop_1 = loop_1.lineTo(0.38108, 0.36161)
loop_1 = loop_1.lineTo(0.39615, 0.36051)
loop_1 = loop_1.lineTo(-0.32528, 0.3633)
loop_1 = loop_1.lineTo(-0.30729, 0.36492)
loop_1 = loop_1.lineTo(-0.2824, 0.36472)
loop_1 = loop_1.lineTo(-0.24636, 0.36583)
loop_1 = loop_1.threePointArc((-0.21094, 0.3649), (-0.18297, 0.36373))
loop_1 = loop_1.threePointArc((-0.14953, 0.36544), (-0.12407, 0.36719))
loop_1 = loop_1.lineTo(-0.10402, 0.36745)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.06)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_52_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_52_interval_0.stl')