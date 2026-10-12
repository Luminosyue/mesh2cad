import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.77146, 0.29357, -0.10793), normal=(-0.95798, -0.28682, 0.00042), xDir=(-0.28682, 0.95798, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.03425, -0.29688)
loop_1 = loop_1.threePointArc((-0.02332, -0.29953), (-0.012, -0.30255))
loop_1 = loop_1.lineTo(0.00047, -0.30561)
loop_1 = loop_1.lineTo(0.02247, -0.30838)
loop_1 = loop_1.lineTo(0.04585, -0.31512)
loop_1 = loop_1.lineTo(0.06273, -0.31431)
loop_1 = loop_1.lineTo(0.08469, -0.31805)
loop_1 = loop_1.lineTo(0.09479, -0.31663)
loop_1 = loop_1.lineTo(0.12727, -0.30207)
loop_1 = loop_1.lineTo(0.14373, -0.30417)
loop_1 = loop_1.lineTo(0.1771, -0.30122)
loop_1 = loop_1.lineTo(0.19523, -0.30311)
loop_1 = loop_1.threePointArc((0.20675, -0.29993), (0.21781, -0.29687))
loop_1 = loop_1.lineTo(-0.03167, -0.29683)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.61)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_24_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_032/refine_under_1/sketch_24_interval_0.stl')