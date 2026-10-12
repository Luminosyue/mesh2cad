import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.98961, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.64947, 0.42)
loop_1 = loop_1.lineTo(-0.56143, 0.41954)
loop_1 = loop_1.lineTo(-0.56154, 0.40774)
loop_1 = loop_1.lineTo(-0.57457, 0.38345)
loop_1 = loop_1.threePointArc((-0.59066, 0.34776), (-0.60511, 0.31331))
loop_1 = loop_1.lineTo(-0.62341, 0.26944)
loop_1 = loop_1.threePointArc((-0.62565, 0.26383), (-0.62722, 0.25846))
loop_1 = loop_1.threePointArc((-0.63281, 0.24051), (-0.63753, 0.22332))
loop_1 = loop_1.threePointArc((-0.64039, 0.20294), (-0.64386, 0.18204))
loop_1 = loop_1.threePointArc((-0.64676, 0.15661), (-0.64927, 0.13238))
loop_1 = loop_1.lineTo(-0.64947, 0.41977)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_47_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_007/refine_over_1/sketch_47_interval_0.stl')