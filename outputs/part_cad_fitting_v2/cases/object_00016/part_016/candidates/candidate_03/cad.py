import cadquery as cq
plane = cq.Plane(origin=[-56.34270010834677, -0.03697192306366161, -36.69514177492694], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(67.25784648300815)
