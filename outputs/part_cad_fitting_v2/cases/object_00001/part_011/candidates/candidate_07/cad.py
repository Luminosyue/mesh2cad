import cadquery as cq
plane = cq.Plane(origin=[-0.09580706385783491, 0.18794317522666354, -0.12050147991745844], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(0.5840180212731594)
