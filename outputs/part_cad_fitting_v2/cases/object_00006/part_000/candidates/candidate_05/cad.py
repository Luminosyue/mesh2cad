import cadquery as cq
plane = cq.Plane(origin=[-0.3781126141548157, 0.1686646633958202, -1.0504192057134223], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(1.0859595928421752).workplane(offset=0.7562252283096313).circle(1.1023848464618289).loft(ruled=True)
