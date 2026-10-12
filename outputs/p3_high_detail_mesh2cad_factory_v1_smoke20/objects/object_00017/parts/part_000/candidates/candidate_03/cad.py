import cadquery as cq
plane = cq.Plane(origin=[-0.004262155365740455, 0.01640237971673049, -0.32750898599624634], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4895918889744669).extrude(0.6550179719924927)
