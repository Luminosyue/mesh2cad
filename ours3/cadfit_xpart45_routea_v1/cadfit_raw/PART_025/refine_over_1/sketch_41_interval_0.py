import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.94748, -0.00159, 0.00222), normal=(0.95328, -0.30207, 0.00239), xDir=(-0.30207, -0.95329, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.13922, -0.32859)
loop_1 = loop_1.lineTo(0.09518, -0.34191)
loop_1 = loop_1.lineTo(0.06346, -0.33173)
loop_1 = loop_1.lineTo(0.03403, -0.3268)
loop_1 = loop_1.lineTo(0.02142, -0.32448)
loop_1 = loop_1.threePointArc((0.0022, -0.32115), (-0.01485, -0.31761))
loop_1 = loop_1.lineTo(-0.03682, -0.31365)
loop_1 = loop_1.lineTo(-0.05581, -0.30983)
loop_1 = loop_1.lineTo(-0.08021, -0.30728)
loop_1 = loop_1.lineTo(-0.09709, -0.30598)
loop_1 = loop_1.lineTo(-0.11221, -0.30485)
loop_1 = loop_1.lineTo(-0.11191, -0.34778)
loop_1 = loop_1.lineTo(0.14536, -0.34778)
loop_1 = loop_1.threePointArc((0.14537, -0.3162), (0.14537, -0.28916))
loop_1 = loop_1.lineTo(0.13922, -0.32859)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.24)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_41_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_41_interval_0.stl')