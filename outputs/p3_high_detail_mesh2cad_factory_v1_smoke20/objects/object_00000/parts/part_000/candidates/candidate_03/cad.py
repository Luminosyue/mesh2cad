import cadquery as cq
plane = cq.Plane(origin=[-0.002319838923795531, -0.06280370676056234, -0.37603244185447693], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3866206073053755).extrude(0.7520648837089539)
