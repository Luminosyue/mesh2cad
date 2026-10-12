import cadquery as cq
plane = cq.Plane(origin=[-3.532440043708711, -2.1444962169732755, -4457.315347880511], xDir=[1.0, 0.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).sphere(4457.319190593722)
