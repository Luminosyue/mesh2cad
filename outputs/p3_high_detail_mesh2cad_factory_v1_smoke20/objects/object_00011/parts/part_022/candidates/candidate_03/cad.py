import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0010882264573598885, 0.0026364326315547783], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.054739611041742804).extrude(1.0)
