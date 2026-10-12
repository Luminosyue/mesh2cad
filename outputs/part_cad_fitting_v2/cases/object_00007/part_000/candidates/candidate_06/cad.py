import cadquery as cq
plane = cq.Plane(origin=[0.035693386817648595, 0.535095790761044, -5.5083539523682346], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(5.599176129321863)
