import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.75726, -0.0108, 0.03087), normal=(0.0419, -0.01236, 0.99905), xDir=(-0.0, 0.99992, 0.01238))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.11852, 1.47999)
loop_1 = loop_1.lineTo(0.0477, 1.47949)
loop_1 = loop_1.threePointArc((0.075, 1.47906), (0.09857, 1.4792))
loop_1 = loop_1.lineTo(0.18046, 1.47947)
loop_1 = loop_1.lineTo(0.18014, 1.35494)
loop_1 = loop_1.lineTo(-0.16003, 1.29279)
loop_1 = loop_1.lineTo(-0.15975, 1.41408)
loop_1 = loop_1.lineTo(-0.12809, 1.46521)
loop_1 = loop_1.lineTo(-0.11872, 1.47966)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_6_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_037/refine_under_1/sketch_6_interval_0.stl')