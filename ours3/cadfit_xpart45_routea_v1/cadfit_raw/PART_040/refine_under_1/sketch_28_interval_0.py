import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.43934, -0.07338, 0.23363), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.31424, -0.6192)
loop_1 = loop_1.lineTo(0.30113, -0.62947)
loop_1 = loop_1.threePointArc((0.29339, -0.6315), (0.286, -0.63365))
loop_1 = loop_1.threePointArc((0.27714, -0.6338), (0.26936, -0.63374))
loop_1 = loop_1.threePointArc((0.26002, -0.6318), (0.25239, -0.63022))
loop_1 = loop_1.lineTo(0.23603, -0.6182)
loop_1 = loop_1.threePointArc((0.22909, -0.6013), (0.22765, -0.59332))
loop_1 = loop_1.threePointArc((0.22801, -0.58441), (0.22844, -0.57658))
loop_1 = loop_1.lineTo(0.2341, -0.56554)
loop_1 = loop_1.threePointArc((0.24391, -0.55617), (0.25021, -0.55231))
loop_1 = loop_1.threePointArc((0.26148, -0.548), (0.26918, -0.54569))
loop_1 = loop_1.threePointArc((0.27822, -0.54511), (0.2861, -0.54463))
loop_1 = loop_1.lineTo(0.30363, -0.54988)
loop_1 = loop_1.threePointArc((0.31012, -0.55445), (0.31681, -0.5593))
loop_1 = loop_1.lineTo(0.31424, -0.6192)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.47)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_28_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_040/refine_under_1/sketch_28_interval_0.stl')