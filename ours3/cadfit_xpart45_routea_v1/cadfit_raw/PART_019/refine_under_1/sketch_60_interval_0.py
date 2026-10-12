import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43374, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.10043, 0.92125)
loop_1 = loop_1.threePointArc((0.16992, 0.9201), (0.23663, 0.92037))
loop_1 = loop_1.lineTo(0.41251, 0.91811)
loop_1 = loop_1.lineTo(0.48439, 0.91669)
loop_1 = loop_1.lineTo(0.50319, 0.91539)
loop_1 = loop_1.lineTo(-0.37961, 0.9163)
loop_1 = loop_1.lineTo(-0.30555, 0.91802)
loop_1 = loop_1.lineTo(-0.19084, 0.91826)
loop_1 = loop_1.threePointArc((-0.13851, 0.91955), (-0.08464, 0.91915))
loop_1 = loop_1.lineTo(0.02266, 0.92018)
loop_1 = loop_1.threePointArc((0.06076, 0.9208), (0.09981, 0.92116))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.95)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_60_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_60_interval_0.stl')