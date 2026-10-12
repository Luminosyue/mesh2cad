import cadquery as cq
plane = cq.Plane(origin=[-0.008097412995994091, 0.0, 0.0], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.3235589638352394).extrude(0.016194825991988182)
