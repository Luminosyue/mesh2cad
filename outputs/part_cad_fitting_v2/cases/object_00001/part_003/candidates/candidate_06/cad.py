import cadquery as cq
plane = cq.Plane(origin=[-0.4738867794630865, 0.8846303589662727, -0.031012596169353826], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(1.2227757891931752)
