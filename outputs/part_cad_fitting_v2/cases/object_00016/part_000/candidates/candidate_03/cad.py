import cadquery as cq
plane = cq.Plane(origin=[-0.0005872405844749891, -0.17554562236978802, 0.0041829168207119655], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.6023509575131967)
