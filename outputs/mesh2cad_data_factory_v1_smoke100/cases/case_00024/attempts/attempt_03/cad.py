import cadquery as cq
plane = cq.Plane(origin=[-0.3332141637802124, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.26771651208400726).extrude(0.6664283275604248)
