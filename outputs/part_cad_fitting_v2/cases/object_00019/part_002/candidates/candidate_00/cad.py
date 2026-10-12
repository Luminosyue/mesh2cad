import cadquery as cq
plane = cq.Plane(origin=[-0.5, 0.0010644631765259968, -0.013629976053895954], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.07495593128901254).extrude(1.0)
