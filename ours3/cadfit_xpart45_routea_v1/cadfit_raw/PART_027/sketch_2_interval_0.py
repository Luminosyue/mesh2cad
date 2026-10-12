import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.3181, 0.18019)
loop_1 = loop_1.lineTo(-0.30671, 0.18008)
loop_1 = loop_1.lineTo(-0.27941, 0.15359)
loop_1 = loop_1.lineTo(-0.2988, 0.12394)
loop_1 = loop_1.lineTo(-0.30988, 0.1229)
loop_1 = loop_1.lineTo(-0.32448, 0.11747)
loop_1 = loop_1.lineTo(-0.33768, 0.11216)
loop_1 = loop_1.lineTo(-0.34652, 0.12264)
loop_1 = loop_1.lineTo(-0.3488, 0.14216)
loop_1 = loop_1.lineTo(-0.34752, 0.15636)
loop_1 = loop_1.lineTo(-0.33957, 0.17002)
loop_1 = loop_1.lineTo(-0.3181, 0.18019)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.1)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_2_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_027/sketch_2_interval_0.stl')