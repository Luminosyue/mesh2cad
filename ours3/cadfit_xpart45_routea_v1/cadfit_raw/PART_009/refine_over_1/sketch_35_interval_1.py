import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.87167, -0.3504, 0.15385), normal=(-0.92121, -0.38906, 6e-05), xDir=(-0.38906, 0.92121, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.33824, 0.67406)
loop_1 = loop_1.lineTo(-0.33829, 0.37325)
loop_1 = loop_1.threePointArc((-0.33587, 0.39415), (-0.33389, 0.41138))
loop_1 = loop_1.threePointArc((-0.33409, 0.43879), (-0.33443, 0.46337))
loop_1 = loop_1.threePointArc((-0.33204, 0.49116), (-0.33026, 0.51536))
loop_1 = loop_1.threePointArc((-0.32988, 0.54342), (-0.32994, 0.56735))
loop_1 = loop_1.lineTo(-0.32742, 0.60762)
loop_1 = loop_1.lineTo(-0.32636, 0.61935)
loop_1 = loop_1.lineTo(-0.31527, 0.64571)
loop_1 = loop_1.lineTo(-0.30954, 0.65833)
loop_1 = loop_1.lineTo(-0.30446, 0.67134)
loop_1 = loop_1.lineTo(-0.33739, 0.67406)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.02)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_35_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_009/refine_over_1/sketch_35_interval_1.stl')