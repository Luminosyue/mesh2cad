import cadquery as cq
plane = cq.Plane(origin=[0.0, 0.0, 0.0], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).box(0.0917588546872139,0.1072353720664978,1.0)
