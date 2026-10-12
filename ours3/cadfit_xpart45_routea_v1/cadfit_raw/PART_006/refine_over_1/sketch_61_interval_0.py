import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.28036, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.95895, 0.52064)
loop_1 = loop_1.lineTo(-0.96941, 0.45571)
loop_1 = loop_1.lineTo(-0.97302, 0.40082)
loop_1 = loop_1.threePointArc((-0.97531, 0.34754), (-0.97626, 0.2968))
loop_1 = loop_1.threePointArc((-0.97661, 0.24511), (-0.97562, 0.19594))
loop_1 = loop_1.lineTo(-0.96692, 0.14473)
loop_1 = loop_1.lineTo(-0.95089, 0.09302)
loop_1 = loop_1.lineTo(-0.92603, 0.0421)
loop_1 = loop_1.threePointArc((-0.91143, 0.02248), (-0.89731, 0.00429))
loop_1 = loop_1.threePointArc((-0.89206, -0.00188), (-0.88702, -0.00802))
loop_1 = loop_1.lineTo(-0.90297, -0.03851)
loop_1 = loop_1.lineTo(-0.92344, -0.0608)
loop_1 = loop_1.lineTo(-0.95302, -0.08043)
loop_1 = loop_1.lineTo(-0.97513, -0.11296)
loop_1 = loop_1.lineTo(-0.9768, -0.13537)
loop_1 = loop_1.lineTo(-0.97523, 0.52064)
loop_1 = loop_1.lineTo(-0.95958, 0.52064)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.52)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_61_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_006/refine_over_1/sketch_61_interval_0.stl')