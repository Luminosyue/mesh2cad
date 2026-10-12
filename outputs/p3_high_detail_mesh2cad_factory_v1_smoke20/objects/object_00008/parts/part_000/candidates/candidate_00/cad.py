import cadquery as cq
plane = cq.Plane(origin=[-0.4678420424461365, -0.1360032096579663, 0.08667970147813266], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.5210892546145738).extrude(0.935684084892273)
