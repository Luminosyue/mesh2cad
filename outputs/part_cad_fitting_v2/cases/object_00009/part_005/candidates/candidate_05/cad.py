import cadquery as cq
plane = cq.Plane(origin=[-0.02200762891388021, -0.009138898084678658, -0.5], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.3314888909557025).workplane(offset=1.0).circle(0.22748662605899145).loft(ruled=True)
