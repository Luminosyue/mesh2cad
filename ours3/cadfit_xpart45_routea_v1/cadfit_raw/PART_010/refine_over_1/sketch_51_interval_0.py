import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, 0.0, -0.42369), normal=(0.0, 0.0, 1.0), xDir=(0.0, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.43327, -0.69219)
loop_1 = loop_1.lineTo(-0.10631, -0.69051)
loop_1 = loop_1.lineTo(-0.10709, -0.57771)
loop_1 = loop_1.lineTo(-0.14975, -0.57816)
loop_1 = loop_1.lineTo(-0.16173, -0.58591)
loop_1 = loop_1.lineTo(-0.18621, -0.60433)
loop_1 = loop_1.threePointArc((-0.18984, -0.61163), (-0.19381, -0.61882))
loop_1 = loop_1.lineTo(-0.22341, -0.65423)
loop_1 = loop_1.threePointArc((-0.23822, -0.6631), (-0.25371, -0.6717))
loop_1 = loop_1.threePointArc((-0.27727, -0.68018), (-0.29578, -0.68528))
loop_1 = loop_1.threePointArc((-0.3168, -0.68725), (-0.33844, -0.68886))
loop_1 = loop_1.threePointArc((-0.38489, -0.69062), (-0.433, -0.69211))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_51_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_51_interval_0.stl')