import cadquery as cq
plane = cq.Plane(origin=[-0.5024411932502163, 0.018372429695177505, -0.045126222439129976], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(0.07495593128901254).extrude(1.0)
