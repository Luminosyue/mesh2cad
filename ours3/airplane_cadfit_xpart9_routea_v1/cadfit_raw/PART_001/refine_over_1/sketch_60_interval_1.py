import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.06804, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.23383, -0.08608)
loop_1 = loop_1.lineTo(0.23399, -0.09609)
loop_1 = loop_1.threePointArc((0.24392, -0.09574), (0.25406, -0.09577))
loop_1 = loop_1.lineTo(0.33375, -0.09336)
loop_1 = loop_1.threePointArc((0.36529, -0.0926), (0.39534, -0.09157))
loop_1 = loop_1.threePointArc((0.42488, -0.09089), (0.45302, -0.08984))
loop_1 = loop_1.lineTo(0.50914, -0.08784)
loop_1 = loop_1.lineTo(0.5441, -0.08637)
loop_1 = loop_1.lineTo(0.23403, -0.08608)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.58)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_60_interval_1.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/airplane_cadfit_xpart9_routea_v1/cadfit_raw/PART_001/refine_over_1/sketch_60_interval_1.stl')