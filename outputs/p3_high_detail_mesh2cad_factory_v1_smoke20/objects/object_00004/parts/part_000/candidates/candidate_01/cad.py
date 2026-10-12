import cadquery as cq
plane = cq.Plane(origin=[0.004393343926210075, -0.007378919986367408, -0.4075619578361511], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.4432571754765055).extrude(0.8151239156723022)
