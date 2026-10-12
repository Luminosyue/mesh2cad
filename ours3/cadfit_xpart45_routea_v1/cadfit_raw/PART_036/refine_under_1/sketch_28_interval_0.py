import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.63008, -0.01888, -0.33323), normal=(0.20985, -2e-05, 0.97773), xDir=(-0.0, 1.0, 2e-05))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.08493, 0.89568)
loop_1 = loop_1.lineTo(-0.08192, 0.91016)
loop_1 = loop_1.lineTo(-0.07507, 0.9431)
loop_1 = loop_1.lineTo(-0.05569, 0.94279)
loop_1 = loop_1.threePointArc((-0.06446, 0.94334), (-0.07226, 0.94401))
loop_1 = loop_1.threePointArc((-0.08279, 0.94484), (-0.09174, 0.94538))
loop_1 = loop_1.threePointArc((-0.10775, 0.94529), (-0.1157, 0.94487))
loop_1 = loop_1.lineTo(-0.13303, 0.93723)
loop_1 = loop_1.lineTo(-0.14139, 0.91845)
loop_1 = loop_1.lineTo(-0.13303, 0.90821)
loop_1 = loop_1.threePointArc((-0.11683, 0.89885), (-0.10829, 0.89717))
loop_1 = loop_1.threePointArc((-0.09925, 0.89649), (-0.09115, 0.89582))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.09)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_036/refine_under_1/sketch_28_interval_0.stl')