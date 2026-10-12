import cadquery as cq
plane = cq.Plane(origin=[0.0020211613170769693, -0.32508984208106995, -0.002355347018480699], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.46762410932591897).extrude(0.6501796841621399)
