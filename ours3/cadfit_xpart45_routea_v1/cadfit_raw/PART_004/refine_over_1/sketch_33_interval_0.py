import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.27048, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.29304, 0.8)
loop_1 = loop_1.lineTo(-0.226, 0.79984)
loop_1 = loop_1.threePointArc((-0.23202, 0.78904), (-0.23759, 0.78416))
loop_1 = loop_1.lineTo(-0.25585, 0.76817)
loop_1 = loop_1.threePointArc((-0.26769, 0.77683), (-0.27554, 0.78314))
loop_1 = loop_1.lineTo(-0.289, 0.79413)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.56)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_33_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_33_interval_0.stl')