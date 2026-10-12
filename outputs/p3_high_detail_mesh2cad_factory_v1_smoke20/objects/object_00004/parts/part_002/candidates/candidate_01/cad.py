import cadquery as cq
plane = cq.Plane(origin=[-0.21646369993686676, 0.0032309204565325045, -0.0005319750740131627], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.460667643409422).extrude(0.4329273998737335)
