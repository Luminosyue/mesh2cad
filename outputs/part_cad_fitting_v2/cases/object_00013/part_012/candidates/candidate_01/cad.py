import cadquery as cq
plane = cq.Plane(origin=[-0.4933243123184222, 0.005143667520536461, -0.007725002107927804], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.020655811442659135).extrude(1.0)
