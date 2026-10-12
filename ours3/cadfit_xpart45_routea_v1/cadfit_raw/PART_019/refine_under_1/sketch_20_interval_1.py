import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.61752, -0.05982, -0.04478), normal=(-0.9999, -0.00024, 0.01412), xDir=(-0.00024, 1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.10627, 0.43904)
loop_1 = loop_1.threePointArc((-0.20103, 0.43814), (-0.29186, 0.43296))
loop_1 = loop_1.lineTo(-0.30332, 0.43307)
loop_1 = loop_1.threePointArc((-0.35597, 0.43282), (-0.41079, 0.43434))
loop_1 = loop_1.threePointArc((-0.50364, 0.43181), (-0.59585, 0.43115))
loop_1 = loop_1.lineTo(0.48803, 0.42801)
loop_1 = loop_1.lineTo(0.4482, 0.43163)
loop_1 = loop_1.lineTo(0.3868, 0.43143)
loop_1 = loop_1.lineTo(0.32532, 0.43577)
loop_1 = loop_1.lineTo(0.26371, 0.43394)
loop_1 = loop_1.lineTo(0.14028, 0.43828)
loop_1 = loop_1.lineTo(0.0787, 0.43623)
loop_1 = loop_1.lineTo(0.06716, 0.43624)
loop_1 = loop_1.threePointArc((0.01007, 0.43644), (-0.04471, 0.43515))
loop_1 = loop_1.lineTo(-0.05625, 0.43614)
loop_1 = loop_1.lineTo(-0.10236, 0.43916)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_20_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_019/refine_under_1/sketch_20_interval_1.stl')