import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.5423, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.8356, 0.21776)
loop_1 = loop_1.lineTo(0.5728, 0.2054)
loop_1 = loop_1.lineTo(0.80808, 0.20493)
loop_1 = loop_1.lineTo(0.81495, 0.19315)
loop_1 = loop_1.lineTo(0.83733, 0.17428)
loop_1 = loop_1.lineTo(0.8356, 0.21774)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.11)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_42_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_013/refine_over_1/sketch_42_interval_0.stl')