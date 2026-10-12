import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.30021, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.54246, 0.64287)
loop_1 = loop_1.lineTo(-0.58656, 0.60927)
loop_1 = loop_1.lineTo(-0.69938, 0.67362)
loop_1 = loop_1.lineTo(-0.49997, 0.67317)
loop_1 = loop_1.threePointArc((-0.51887, 0.65969), (-0.53675, 0.64665))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.31)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_40_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_010/refine_over_1/sketch_40_interval_1.stl')