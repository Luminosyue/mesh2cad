import cadquery as cq
plane = cq.Plane(origin=[0.004554705927453773, 0.006257088784285708, -0.3243243098258972], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.45713056225159726).extrude(0.6486486196517944)
