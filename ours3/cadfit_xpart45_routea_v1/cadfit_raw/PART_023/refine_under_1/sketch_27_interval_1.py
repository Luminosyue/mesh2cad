import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.49316, -0.21944, 0.01636), normal=(0.86268, -0.50576, -0.00026), xDir=(-0.50576, -0.86268, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.28829, 0.54995)
loop_1 = loop_1.lineTo(-0.28678, 0.33876)
loop_1 = loop_1.lineTo(-0.29696, 0.3391)
loop_1 = loop_1.threePointArc((-0.29744, 0.38354), (-0.29741, 0.42742))
loop_1 = loop_1.lineTo(-0.29737, 0.53418)
loop_1 = loop_1.threePointArc((-0.29717, 0.54465), (-0.29704, 0.55285))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_27_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_023/refine_under_1/sketch_27_interval_1.stl')