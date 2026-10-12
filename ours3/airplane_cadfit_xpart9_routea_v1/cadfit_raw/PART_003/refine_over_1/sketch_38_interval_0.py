import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.89208, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.11995, -0.31479)
loop_1 = loop_1.lineTo(0.02015, -0.31869)
loop_1 = loop_1.lineTo(0.0205, -0.16664)
loop_1 = loop_1.threePointArc((0.02574, -0.1769), (0.0308, -0.18761))
loop_1 = loop_1.threePointArc((0.04092, -0.20871), (0.05073, -0.22877))
loop_1 = loop_1.lineTo(0.059, -0.24483)
loop_1 = loop_1.lineTo(0.08163, -0.28004)
loop_1 = loop_1.lineTo(0.11823, -0.31392)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.25)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_38_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_003/refine_over_1/sketch_38_interval_0.stl')