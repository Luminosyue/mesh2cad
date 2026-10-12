import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.48495, -0.11223, 0.24755), normal=(0.99896, 0.00409, 0.04543), xDir=(0.0041, -0.99999, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24213, 0.27693)
loop_1 = loop_1.threePointArc((-0.24359, 0.25572), (-0.24458, 0.23533))
loop_1 = loop_1.lineTo(-0.25392, 0.05145)
loop_1 = loop_1.lineTo(-0.24604, 0.06896)
loop_1 = loop_1.lineTo(-0.23967, 0.08839)
loop_1 = loop_1.lineTo(-0.23102, 0.11161)
loop_1 = loop_1.lineTo(-0.22706, 0.13526)
loop_1 = loop_1.lineTo(-0.22657, 0.14866)
loop_1 = loop_1.lineTo(-0.22804, 0.17296)
loop_1 = loop_1.threePointArc((-0.23072, 0.19148), (-0.23285, 0.20859))
loop_1 = loop_1.lineTo(-0.23551, 0.22509)
loop_1 = loop_1.lineTo(-0.2397, 0.25983)
loop_1 = loop_1.threePointArc((-0.24099, 0.26843), (-0.24187, 0.27505))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_51_interval_0.stl')