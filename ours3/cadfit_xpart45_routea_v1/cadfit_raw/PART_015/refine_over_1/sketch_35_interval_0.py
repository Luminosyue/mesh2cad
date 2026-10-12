import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.68009, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.34037, -0.25691)
loop_1 = loop_1.lineTo(-0.31982, -0.25677)
loop_1 = loop_1.lineTo(-0.65929, -0.25267)
loop_1 = loop_1.lineTo(-0.63181, -0.25861)
loop_1 = loop_1.lineTo(-0.61252, -0.26113)
loop_1 = loop_1.threePointArc((-0.56904, -0.25967), (-0.52398, -0.25869))
loop_1 = loop_1.lineTo(-0.45729, -0.25744)
loop_1 = loop_1.lineTo(-0.35748, -0.25715)
loop_1 = loop_1.threePointArc((-0.34909, -0.25702), (-0.3406, -0.25691))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.55)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_35_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_015/refine_over_1/sketch_35_interval_0.stl')