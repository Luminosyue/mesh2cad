import cadquery as cq
plane = cq.Plane(origin=[-0.008008127875468285, -0.132273331284523, 0.04926701051755586], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.3681403111531423).extrude(0.264546662569046)
