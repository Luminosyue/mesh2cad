import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.12322, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.26231, 0.07741)
loop_1 = loop_1.lineTo(-0.11643, 0.07704)
loop_1 = loop_1.lineTo(-0.11851, 0.05642)
loop_1 = loop_1.lineTo(-0.12771, 0.03886)
loop_1 = loop_1.threePointArc((-0.13392, 0.03449), (-0.13811, 0.03194))
loop_1 = loop_1.threePointArc((-0.15586, 0.02574), (-0.16438, 0.02485))
loop_1 = loop_1.threePointArc((-0.1758, 0.02483), (-0.18755, 0.02498))
loop_1 = loop_1.threePointArc((-0.19961, 0.02523), (-0.21106, 0.02529))
loop_1 = loop_1.threePointArc((-0.21936, 0.02556), (-0.22786, 0.02604))
loop_1 = loop_1.threePointArc((-0.24262, 0.02922), (-0.25132, 0.03236))
loop_1 = loop_1.lineTo(-0.26725, 0.05713)
loop_1 = loop_1.threePointArc((-0.26817, 0.06422), (-0.26881, 0.07151))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.28)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_61_interval_0.stl')