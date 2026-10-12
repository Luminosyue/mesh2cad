import cadquery as cq
plane = cq.Plane(origin=[-58.031559700937045, 9.017082550358076, 4042.611903999258], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(4043.0932934183347)
