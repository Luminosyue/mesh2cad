import cadquery as cq
plane = cq.Plane(origin=[-0.003419875410307832, 0.011303269627143018, -0.2017243355512619], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.27411658956167406).extrude(0.4034486711025238)
