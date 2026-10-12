import cadquery as cq
plane = cq.Plane(origin=[5.929774174688596e-05, -0.014285707846283913, -0.2963013019888257], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.4157284134196006).extrude(0.028571415692567825)
