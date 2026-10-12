import cadquery as cq
p0_plane = cq.Plane(origin=[0.0011762298998142869, -0.5, -0.003944646452231547], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
p0_result = cq.Workplane(p0_plane).circle(0.012911188650918198).extrude(1.0)
assembly_shape = cq.Compound.makeCompound([p0_result.val().scale(0.6960542351007462).translate([0.07326677069067955, 0.11831905692815779, -0.08128335326910019])])
result = cq.Workplane("XY").newObject([assembly_shape])
