import cadquery as cq
plane = cq.Plane(origin=[-0.09005715698003769, 0.1105029755279816, -0.7261233537568654], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.7752817339177838).extrude(0.18011431396007538)
