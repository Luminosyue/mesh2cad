import cadquery as cq
plane = cq.Plane(origin=[-0.3781126141548157, 0.1686646633958202, -1.0504192057134223], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(1.1007137662081206).extrude(0.7562252283096313)
