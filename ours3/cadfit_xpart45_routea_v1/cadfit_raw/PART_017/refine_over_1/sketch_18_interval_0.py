import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.08874, -0.05945, -0.0423), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.24126, 0.54474)
loop_1 = loop_1.lineTo(-0.19823, 0.5683)
loop_1 = loop_1.lineTo(-0.16307, 0.58578)
loop_1 = loop_1.threePointArc((-0.1415, 0.59469), (-0.12244, 0.6023))
loop_1 = loop_1.threePointArc((-0.10332, 0.60923), (-0.08578, 0.61543))
loop_1 = loop_1.lineTo(-0.04626, 0.62561)
loop_1 = loop_1.threePointArc((-0.02465, 0.62987), (-0.00852, 0.6333))
loop_1 = loop_1.lineTo(0.0108, 0.63588)
loop_1 = loop_1.lineTo(0.02124, 0.63716)
loop_1 = loop_1.lineTo(0.04767, 0.64016)
loop_1 = loop_1.lineTo(0.07093, 0.64299)
loop_1 = loop_1.lineTo(-0.24126, 0.64376)
loop_1 = loop_1.lineTo(-0.24126, 0.54538)
loop_1 = loop_1.lineTo(-0.26801, 0.53072)
loop_1 = loop_1.threePointArc((-0.25862, 0.53474), (-0.24468, 0.54282))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.35)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_18_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_017/refine_over_1/sketch_18_interval_0.stl')