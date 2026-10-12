import cadquery as cq
plane = cq.Plane(origin=[-0.2335142344236374, -0.08431669848021067, 0.07467227302980933], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.40863876025654344).extrude(0.4670284688472748)
