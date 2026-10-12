import cadquery as cq
plane = cq.Plane(origin=[-22.85891056201734, 0.07594328750842357, -0.8542739963019588], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(22.91884301787415)
