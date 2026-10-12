import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.06556, -0.27543, 0.07199), normal=(0.56482, 0.82522, -3e-05), xDir=(0.82522, -0.56482, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04572, -0.05164)
loop_1 = loop_1.lineTo(-0.06163, -0.05206)
loop_1 = loop_1.threePointArc((-0.07434, -0.05259), (-0.08499, -0.05322))
loop_1 = loop_1.lineTo(-0.09731, -0.05756)
loop_1 = loop_1.lineTo(-0.10321, -0.08185)
loop_1 = loop_1.lineTo(-0.09809, -0.09731)
loop_1 = loop_1.lineTo(-0.07584, -0.10711)
loop_1 = loop_1.threePointArc((-0.04885, -0.10651), (-0.02265, -0.1063))
loop_1 = loop_1.lineTo(0.01884, -0.09691)
loop_1 = loop_1.threePointArc((0.02157, -0.09071), (0.02418, -0.08476))
loop_1 = loop_1.lineTo(0.02357, -0.06865)
loop_1 = loop_1.threePointArc((0.01865, -0.062), (0.01353, -0.05507))
loop_1 = loop_1.threePointArc((0.00583, -0.0528), (-0.00011, -0.05105))
loop_1 = loop_1.threePointArc((-0.00746, -0.05018), (-0.01259, -0.04958))
loop_1 = loop_1.lineTo(-0.03814, -0.05129)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.03)

result = solid_1
cq.exporters.export(result, '/data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_39_interval_0.stl')
print('Successfully exported 1 solid to /data/home/cuiyuehan/project/mesh2cad/ours3/cadfit_xpart45_routea_v1/cadfit_raw/PART_025/refine_over_1/sketch_39_interval_0.stl')