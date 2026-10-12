import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.3247, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.16179, -0.62596)
loop_1 = loop_1.lineTo(-0.16223, -0.8593)
loop_1 = loop_1.threePointArc((-0.16305, -0.84804), (-0.16319, -0.84553))
loop_1 = loop_1.lineTo(-0.16354, -0.82412)
loop_1 = loop_1.lineTo(-0.16277, -0.79746)
loop_1 = loop_1.threePointArc((-0.16294, -0.7734), (-0.16279, -0.74851))
loop_1 = loop_1.lineTo(-0.16425, -0.72331)
loop_1 = loop_1.lineTo(-0.17041, -0.69711)
loop_1 = loop_1.lineTo(-0.17455, -0.6847)
loop_1 = loop_1.lineTo(-0.18968, -0.6749)
loop_1 = loop_1.lineTo(-0.18855, -0.64711)
loop_1 = loop_1.lineTo(-0.1619, -0.62608)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.33)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_59_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_59_interval_0.stl')