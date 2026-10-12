import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.19, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.50711, -0.03525)
loop_1 = loop_1.lineTo(-0.57995, -0.03667)
loop_1 = loop_1.lineTo(-0.58498, -0.05858)
loop_1 = loop_1.lineTo(-0.57633, -0.07298)
loop_1 = loop_1.lineTo(-0.55875, -0.08712)
loop_1 = loop_1.threePointArc((-0.56526, -0.0887), (-0.57135, -0.09031))
loop_1 = loop_1.lineTo(-0.58677, -0.10414)
loop_1 = loop_1.lineTo(-0.56096, -0.14036)
loop_1 = loop_1.lineTo(-0.54129, -0.14929)
loop_1 = loop_1.lineTo(-0.52144, -0.13555)
loop_1 = loop_1.lineTo(-0.5088, -0.11304)
loop_1 = loop_1.threePointArc((-0.50503, -0.10558), (-0.50355, -0.10247))
loop_1 = loop_1.lineTo(-0.51347, -0.08766)
loop_1 = loop_1.threePointArc((-0.50577, -0.07947), (-0.49778, -0.07293))
loop_1 = loop_1.lineTo(-0.4923, -0.05814)
loop_1 = loop_1.lineTo(-0.50211, -0.0433)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.2)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_49_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_029/refine_under_1/sketch_49_interval_0.stl')