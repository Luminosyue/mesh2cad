import cadquery as cq
plane = cq.Plane(origin=[-0.06250002235174179, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.28125007823109627).extrude(0.12500004470348358)
