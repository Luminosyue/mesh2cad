import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.75726, -0.0108, 0.03087), normal=(0.0419, -0.01236, 0.99905), xDir=(-0.0, 0.99992, 0.01238))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.00724, 0.74362)
loop_1 = loop_1.lineTo(0.01317, 0.74002)
loop_1 = loop_1.lineTo(0.02682, 0.74058)
loop_1 = loop_1.threePointArc((0.03809, 0.75194), (0.04046, 0.75593))
loop_1 = loop_1.lineTo(0.04307, 0.7743)
loop_1 = loop_1.lineTo(0.04188, 0.78655)
loop_1 = loop_1.lineTo(0.03047, 0.8016)
loop_1 = loop_1.lineTo(0.01221, 0.79894)
loop_1 = loop_1.lineTo(0.00121, 0.80081)
loop_1 = loop_1.lineTo(0.00391, 0.78305)
loop_1 = loop_1.threePointArc((0.00299, 0.76821), (0.00195, 0.76169))
loop_1 = loop_1.threePointArc((-0.00101, 0.75426), (-0.00423, 0.74735))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.04)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_27_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_27_interval_0.stl')