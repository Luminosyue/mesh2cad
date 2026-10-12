import cadquery as cq
plane = cq.Plane(origin=[-0.10235861022919136, -21.026055881058863, -0.47519060831324716], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(20.996377956848242)
