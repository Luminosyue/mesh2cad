import cadquery as cq
plane = cq.Plane(origin=[0.01609534843127522, -1.177628458415552e-05, -0.5074554670788843], xDir=[0.0, -1.0, 0.0], normal=[-0.009999833334166664, 0.0, 0.9999500004166653])
result = cq.Workplane(plane).circle(np.float64(0.03779401710055711)).extrude(np.float64(0.9656054162575665))
