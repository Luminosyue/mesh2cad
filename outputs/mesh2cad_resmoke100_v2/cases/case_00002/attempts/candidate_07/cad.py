import cadquery as cq
plane = cq.Plane(origin=[-8.04959034390676e-06, 0.024912504822907244, -0.022976449039620716], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.3591695680474425)
