import cadquery as cq
plane = cq.Plane(origin=[0.014460774226738663, -0.0002907205091484305, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.03267344802748406).extrude(1.0)
