import cadquery as cq
plane = cq.Plane(origin=[0.0032005127534750306, 0.014252974522667827, -0.19171173307047415], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.3977606975522712)
