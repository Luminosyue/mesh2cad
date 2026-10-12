import cadquery as cq
plane = cq.Plane(origin=[-0.15256395944034415, 0.06308642063390706, -0.34770655632019043], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.314967217874026).extrude(0.6954131126403809)
