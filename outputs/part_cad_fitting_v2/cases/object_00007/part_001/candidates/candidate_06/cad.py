import cadquery as cq
plane = cq.Plane(origin=[0.028411590192045543, 5.506826522739047, -0.8032423370805829], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(5.604089307888967)
