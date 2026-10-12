import cadquery as cq
plane = cq.Plane(origin=[-0.00040109204354583813, 0.0002225773622792819, -0.5290374034561257], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03715897833195939)).extrude(np.float64(1.0))
