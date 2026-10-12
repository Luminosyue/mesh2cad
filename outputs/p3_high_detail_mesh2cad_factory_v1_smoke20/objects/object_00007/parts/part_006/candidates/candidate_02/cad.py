import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.005951551172180314, -0.004629677011733237], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.04117247734528011).extrude(1.0)
