import cadquery as cq
plane = cq.Plane(origin=[0.02943349415815417, -0.0014857105694385379, -0.5296052821884705], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.19719969416687286)).extrude(np.float64(1.0))
