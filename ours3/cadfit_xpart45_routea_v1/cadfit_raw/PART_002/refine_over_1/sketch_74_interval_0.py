import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.21456, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.56752, -0.55023)
loop_1 = loop_1.lineTo(-0.56695, -0.81)
loop_1 = loop_1.lineTo(-0.55118, -0.80982)
loop_1 = loop_1.lineTo(-0.55657, -0.7649)
loop_1 = loop_1.lineTo(-0.54958, -0.72785)
loop_1 = loop_1.lineTo(-0.52621, -0.69142)
loop_1 = loop_1.lineTo(-0.53442, -0.65342)
loop_1 = loop_1.lineTo(-0.55095, -0.6165)
loop_1 = loop_1.lineTo(-0.56179, -0.57838)
loop_1 = loop_1.threePointArc((-0.56444, -0.56425), (-0.56743, -0.55096))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.18)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_74_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_002/refine_over_1/sketch_74_interval_0.stl')