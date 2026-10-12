import cadquery as cq
plane = cq.Plane(origin=[-0.3561772448858165, 0.04578967916268409, 0.024045518399549264], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(np.float64(0.3813476555606213)).extrude(np.float64(0.7070083022117615))
