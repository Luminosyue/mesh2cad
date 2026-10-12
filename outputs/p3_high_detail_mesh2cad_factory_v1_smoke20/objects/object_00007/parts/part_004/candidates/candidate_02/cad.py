import cadquery as cq
plane = cq.Plane(origin=[-0.43055540323257446, -0.0036298046463398292, 0.0893395520570417], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.38422315987522204).extrude(0.8611108064651489)
