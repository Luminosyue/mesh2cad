import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06267, 0.71878, -0.27295), normal=(0.0, -0.88735, 0.46109), xDir=(-1.0, -0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03692, 0.04893)
loop_1 = loop_1.lineTo(-0.08127, 0.04663)
loop_1 = loop_1.lineTo(-0.21079, 0.04672)
loop_1 = loop_1.lineTo(-0.25119, 0.04546)
loop_1 = loop_1.threePointArc((-0.2751, 0.04315), (-0.29714, 0.04158))
loop_1 = loop_1.lineTo(0.31881, 0.03329)
loop_1 = loop_1.lineTo(0.29551, 0.04288)
loop_1 = loop_1.lineTo(0.26412, 0.04361)
loop_1 = loop_1.lineTo(0.21879, 0.04367)
loop_1 = loop_1.threePointArc((0.15276, 0.04422), (0.0855, 0.04702))
loop_1 = loop_1.threePointArc((0.0232, 0.04846), (-0.03092, 0.04885))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_016/refine_under_1/sketch_24_interval_0.stl')