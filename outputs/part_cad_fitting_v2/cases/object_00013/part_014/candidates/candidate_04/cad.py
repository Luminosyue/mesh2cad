import cadquery as cq
plane = cq.Plane(origin=[-0.5, -0.0016812717613386386, -0.009001473450413985], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.02404746404149785).workplane(offset=1.0).circle(0.024158212579881558).loft(ruled=True)
