import cadquery as cq
plane = cq.Plane(origin=[-0.0036621025332100655, 0.0026666281576973538, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.06776917928027229).workplane(offset=1.0).circle(0.05605824438207899).loft(ruled=True)
