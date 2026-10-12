import cadquery as cq
plane = cq.Plane(origin=[-0.3483240306377411, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.4520616829395294).extrude(0.6966480612754822)
