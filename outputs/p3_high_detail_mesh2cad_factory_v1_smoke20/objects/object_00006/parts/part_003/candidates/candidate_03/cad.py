import cadquery as cq
plane = cq.Plane(origin=[-0.0010239796805223689, 0.006834940320420007, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.32439379488971076).extrude(1.0)
