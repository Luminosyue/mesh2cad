import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.48361, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.64316, -0.47133)
loop_1 = loop_1.threePointArc((-0.63642, -0.45595), (-0.63065, -0.44091))
loop_1 = loop_1.lineTo(-0.61625, -0.42245)
loop_1 = loop_1.threePointArc((-0.59815, -0.41069), (-0.57931, -0.39922))
loop_1 = loop_1.lineTo(-0.526, -0.41531)
loop_1 = loop_1.lineTo(-0.31801, -0.35977)
loop_1 = loop_1.threePointArc((-0.30734, -0.36258), (-0.29725, -0.36393))
loop_1 = loop_1.lineTo(-0.26696, -0.36876)
loop_1 = loop_1.threePointArc((-0.25123, -0.38482), (-0.24061, -0.39529))
loop_1 = loop_1.lineTo(-0.2159, -0.42077)
loop_1 = loop_1.threePointArc((-0.19376, -0.45196), (-0.1724, -0.4812))
loop_1 = loop_1.threePointArc((-0.16389, -0.49287), (-0.15503, -0.50301))
loop_1 = loop_1.lineTo(-0.13327, -0.52936)
loop_1 = loop_1.lineTo(-0.67535, -0.5281)
loop_1 = loop_1.threePointArc((-0.66489, -0.5112), (-0.65586, -0.49486))
loop_1 = loop_1.lineTo(-0.64409, -0.47372)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.88)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_71_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_71_interval_0.stl')