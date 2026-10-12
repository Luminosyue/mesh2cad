import cadquery as cq
import math

plane_1 = cq.Plane(origin=(0.0, -0.99, 0.0), normal=(0.0, 1.0, 0.0), xDir=(1.0, 0.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-0.04736, 0.03678)
loop_1 = loop_1.threePointArc((-0.06182, 0.03291), (-0.06637, 0.03072))
loop_1 = loop_1.threePointArc((-0.07636, 0.02342), (-0.07678, 0.02267))
loop_1 = loop_1.lineTo(-0.08523, 0.00276)
loop_1 = loop_1.lineTo(-0.07509, -0.02599)
loop_1 = loop_1.lineTo(-0.05599, -0.03281)
loop_1 = loop_1.threePointArc((-0.04225, -0.03579), (-0.0376, -0.03493))
loop_1 = loop_1.lineTo(-0.01912, -0.02312)
loop_1 = loop_1.threePointArc((-0.01416, -0.00887), (-0.0139, -0.0042))
loop_1 = loop_1.lineTo(-0.01808, 0.01467)
loop_1 = loop_1.lineTo(-0.02902, 0.02862)
loop_1 = loop_1.threePointArc((-0.04286, 0.03543), (-0.04728, 0.03674))
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.98)

result = solid_1
