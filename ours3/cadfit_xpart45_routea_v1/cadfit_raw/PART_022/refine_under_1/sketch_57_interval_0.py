import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.18), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.891, -0.45787)
loop_1 = loop_1.lineTo(-0.72509, -0.6675)
loop_1 = loop_1.threePointArc((-0.71502, -0.67714), (-0.70516, -0.6859))
loop_1 = loop_1.lineTo(-0.72639, -0.66668)
loop_1 = loop_1.threePointArc((-0.73429, -0.65873), (-0.74219, -0.65045))
loop_1 = loop_1.lineTo(-0.82112, -0.5617)
loop_1 = loop_1.threePointArc((-0.83286, -0.54904), (-0.84455, -0.53567))
loop_1 = loop_1.threePointArc((-0.85053, -0.52766), (-0.85626, -0.51923))
loop_1 = loop_1.lineTo(-0.86943, -0.50043)
loop_1 = loop_1.lineTo(-0.88331, -0.4739)
loop_1 = loop_1.lineTo(-0.89092, -0.45805)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.45)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_57_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_022/refine_under_1/sketch_57_interval_0.stl')