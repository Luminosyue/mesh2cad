import cadquery as cq
plane = cq.Plane(origin=[-0.006124460578835414, -0.5, 0.00034719514557765856], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.023982735880503425).extrude(1.0)
