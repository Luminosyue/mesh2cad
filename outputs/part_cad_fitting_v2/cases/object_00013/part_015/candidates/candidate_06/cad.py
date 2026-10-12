import cadquery as cq
plane = cq.Plane(origin=[-0.038064581438611224, 12.58997203874375, 0.2055090578260708], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(12.605588109125515)
