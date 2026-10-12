import cadquery as cq
plane = cq.Plane(origin=[0.3840100843051102, -94.7755197479353, -0.06638078391551971], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(94.81665451223003).workplane(offset=0.13276156783103943).circle(94.74636896443701).loft(ruled=True)
