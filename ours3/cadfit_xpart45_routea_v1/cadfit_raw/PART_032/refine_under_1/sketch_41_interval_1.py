import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.18272, -0.37135, -0.05837), normal=(0.40072, -0.9162, -0.00057), xDir=(-0.9162, -0.40072, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.35895, 0.17143)
loop_1 = loop_1.lineTo(-0.36877, 0.15876)
loop_1 = loop_1.lineTo(-0.37849, 0.13909)
loop_1 = loop_1.lineTo(-0.37755, 0.12866)
loop_1 = loop_1.lineTo(-0.37286, 0.09001)
loop_1 = loop_1.lineTo(-0.36874, 0.06154)
loop_1 = loop_1.threePointArc((-0.36674, 0.05216), (-0.36526, 0.04532))
loop_1 = loop_1.threePointArc((-0.36299, 0.02039), (-0.36095, -0.00156))
loop_1 = loop_1.lineTo(-0.35927, -0.0462)
loop_1 = loop_1.lineTo(-0.35895, 0.16923)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.26)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_41_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_41_interval_1.stl')