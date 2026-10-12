import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.97021, 0.34768, 0.04489), normal=(-0.93656, -0.35052, 0.0004), xDir=(-0.35052, 0.93656, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.08096, -0.01629)
loop_1 = loop_1.lineTo(-0.01027, -0.04659)
loop_1 = loop_1.lineTo(-0.03695, -0.06458)
loop_1 = loop_1.lineTo(-0.04529, -0.10246)
loop_1 = loop_1.lineTo(-0.04867, -0.14045)
loop_1 = loop_1.threePointArc((-0.04667, -0.19491), (-0.04566, -0.24385))
loop_1 = loop_1.lineTo(-0.04246, -0.38487)
loop_1 = loop_1.lineTo(-0.04225, -0.40291)
loop_1 = loop_1.lineTo(-0.03674, -0.44133)
loop_1 = loop_1.lineTo(-0.02643, -0.47903)
loop_1 = loop_1.lineTo(-0.01439, -0.4863)
loop_1 = loop_1.lineTo(-0.00171, -0.4922)
loop_1 = loop_1.lineTo(0.01477, -0.49806)
loop_1 = loop_1.lineTo(0.03168, -0.50277)
loop_1 = loop_1.lineTo(0.08089, -0.51867)
loop_1 = loop_1.lineTo(0.08096, -0.02025)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.07)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_8_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_005/refine_over_1/sketch_8_interval_0.stl')