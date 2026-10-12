import cadquery as cq
plane = cq.Plane(origin=[-0.09187879322116649, -0.02735617198050022, 0.9025217914620758], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(1.11184582665755).extrude(0.05471234396100044)
