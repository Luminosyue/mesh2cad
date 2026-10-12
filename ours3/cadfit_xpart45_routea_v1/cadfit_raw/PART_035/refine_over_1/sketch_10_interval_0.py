import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.57373, 0.58362, 0.04528), normal=(-0.06605, -0.99781, -0.00203), xDir=(-0.99782, 0.06605, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.22213, -0.19322)
loop_1 = loop_1.lineTo(-0.2221, -0.17377)
loop_1 = loop_1.lineTo(-0.21713, -0.19212)
loop_1 = loop_1.lineTo(-0.22206, -0.15362)
loop_1 = loop_1.lineTo(-0.22204, -0.12818)
loop_1 = loop_1.lineTo(-0.22177, -0.10443)
loop_1 = loop_1.lineTo(-0.22569, -0.08134)
loop_1 = loop_1.lineTo(-0.23113, -0.06264)
loop_1 = loop_1.lineTo(-0.23349, -0.20543)
loop_1 = loop_1.lineTo(-0.20695, -0.20541)
loop_1 = loop_1.lineTo(-0.22213, -0.19322)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.87)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_10_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_035/refine_over_1/sketch_10_interval_0.stl')