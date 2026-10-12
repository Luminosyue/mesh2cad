import cadquery as cq
plane = cq.Plane(origin=[-0.33923250436782837, -0.0038301410243730682, 0.004383700949454777], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4474582504280749).extrude(0.6784650087356567)
