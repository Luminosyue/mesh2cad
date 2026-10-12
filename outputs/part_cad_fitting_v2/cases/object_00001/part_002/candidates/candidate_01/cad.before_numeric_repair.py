import cadquery as cq
plane = cq.Plane(origin=[-0.013072497987170823, 0.044712157744738364, -0.518090980052948], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(np.float64(0.48900276803704873)).extrude(np.float64(0.876181960105896))
