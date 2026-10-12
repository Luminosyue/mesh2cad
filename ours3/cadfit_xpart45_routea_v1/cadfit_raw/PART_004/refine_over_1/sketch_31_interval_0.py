import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.32048, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.40323, -0.85877)
loop_1 = loop_1.lineTo(-0.39792, -0.38149)
loop_1 = loop_1.lineTo(-0.36775, 0.82897)
loop_1 = loop_1.threePointArc((-0.38475, 0.81147), (-0.39851, 0.79376))
loop_1 = loop_1.threePointArc((-0.40065, 0.77043), (-0.40017, 0.7493))
loop_1 = loop_1.threePointArc((-0.40211, -0.03014), (-0.40191, -0.77726))
loop_1 = loop_1.threePointArc((-0.40033, -0.81372), (-0.40088, -0.85053))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_31_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_004/refine_over_1/sketch_31_interval_0.stl')