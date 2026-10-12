import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.10754, 0.12117, -0.16068), normal=(-0.0, 0.0, 1.0), xDir=(0.0, 1.0, -0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(-1.12117, -0.33543)
loop_1 = loop_1.lineTo(-0.37905, -0.33543)
loop_1 = loop_1.lineTo(-0.3326, -0.8433)
loop_1 = loop_1.lineTo(0.18018, -0.29538)
loop_1 = loop_1.lineTo(0.87883, -0.04928)
loop_1 = loop_1.lineTo(0.38228, 0.14114)
loop_1 = loop_1.lineTo(0.62752, 0.62822)
loop_1 = loop_1.lineTo(-0.00991, 0.50698)
loop_1 = loop_1.lineTo(-0.50092, 0.4909)
loop_1 = loop_1.lineTo(-0.50092, 0.04664)
loop_1 = loop_1.lineTo(-1.09502, -0.31932)
loop_1 = loop_1.lineTo(-1.12117, -0.33543)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(0.32)

result = solid_1
