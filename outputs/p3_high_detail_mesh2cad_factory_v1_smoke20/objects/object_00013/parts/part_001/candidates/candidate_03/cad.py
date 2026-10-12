import cadquery as cq
plane = cq.Plane(origin=[-0.10547568649053574, -0.005308009548185999, -0.05528737606561813], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.3288675221832458).extrude(0.21095137298107147)
