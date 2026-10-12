import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.02537, 0.28464, 0.12), normal=(-0.0, -0.0, -1.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.07996, 0.08876)
loop_1 = loop_1.threePointArc((-0.08093, 0.13106), (-0.08219, 0.17165))
loop_1 = loop_1.threePointArc((-0.08336, 0.19357), (-0.08465, 0.21179))
loop_1 = loop_1.threePointArc((-0.08663, 0.23928), (-0.08805, 0.25794))
loop_1 = loop_1.lineTo(-0.09193, 0.28303)
loop_1 = loop_1.lineTo(-0.07828, -0.00403)
loop_1 = loop_1.lineTo(-0.07909, 0.06101)
loop_1 = loop_1.threePointArc((-0.07951, 0.07484), (-0.07985, 0.08624))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.3)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_043/refine_over_1/sketch_2_interval_0.stl')