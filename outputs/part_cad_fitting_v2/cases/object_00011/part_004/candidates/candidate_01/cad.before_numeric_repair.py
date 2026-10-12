import cadquery as cq
plane = cq.Plane(origin=[-0.00015953954409835645, -0.002030430706878234, -0.5162765813172544], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.03837753016277738)).extrude(np.float64(1.0))
