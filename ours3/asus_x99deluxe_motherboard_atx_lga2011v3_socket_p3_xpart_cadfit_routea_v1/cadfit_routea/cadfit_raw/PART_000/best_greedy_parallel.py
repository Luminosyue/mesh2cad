import cadquery as cq
import math

plane_1 = cq.Plane(origin=(-0.98, 0.0, 0.0), normal=(1.0, 0.0, 0.0), xDir=(0.0, -1.0, 0.0))
sketch_1 = cq.Workplane(plane_1)
loop_1 = sketch_1.moveTo(0.21253, 0.77708)
loop_1 = loop_1.threePointArc((0.22466, 0.76274), (0.22734, 0.74339))
loop_1 = loop_1.threePointArc((0.23309, 0.43032), (0.23474, 0.10556))
loop_1 = loop_1.threePointArc((0.23672, -0.31499), (0.23535, -0.75171))
loop_1 = loop_1.threePointArc((0.23321, -0.76626), (0.22974, -0.77966))
loop_1 = loop_1.threePointArc((0.22286, -0.78588), (0.21542, -0.78973))
loop_1 = loop_1.lineTo(0.0376, -0.78251)
loop_1 = loop_1.lineTo(-0.1859, -0.78147)
loop_1 = loop_1.lineTo(-0.19994, -0.7717)
loop_1 = loop_1.threePointArc((-0.20411, -0.7092), (-0.20509, -0.64525))
loop_1 = loop_1.threePointArc((-0.2102, -0.43858), (-0.21654, -0.24145))
loop_1 = loop_1.threePointArc((-0.22437, 0.17535), (-0.23164, 0.608))
loop_1 = loop_1.threePointArc((-0.23097, 0.67885), (-0.22954, 0.75123))
loop_1 = loop_1.threePointArc((-0.2221, 0.76368), (-0.2168, 0.76841))
loop_1 = loop_1.threePointArc((-0.0689, 0.77488), (0.07626, 0.7754))
loop_1 = loop_1.lineTo(0.21129, 0.77718)
loop_1 = loop_1.close()
sketch_1=sketch_1.add(loop_1)
solid_1 = sketch_1.extrude(1.96)

result = solid_1