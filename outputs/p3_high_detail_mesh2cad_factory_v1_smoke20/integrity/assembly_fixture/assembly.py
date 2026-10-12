import cadquery as cq
p0_result = cq.Workplane('XY').box(1, 0.6, 0.4)
p1_result = cq.Workplane('XY').box(1, 0.6, 0.4)
assembly_shape = cq.Compound.makeCompound([p0_result.val().scale(0.7).translate([0.1, -0.2, 0.3]), p1_result.val().scale(0.25).translate([-0.6, 0.4, -0.1])])
result = cq.Workplane("XY").newObject([assembly_shape])
