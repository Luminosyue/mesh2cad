import cadquery as cq
plane = cq.Plane(origin=[-0.5932214751254337, 0.1111876095536432, -0.34770655632019043], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.7555261689880007).workplane(offset=0.6954131126403809).circle(0.7457909296061124).loft(ruled=True)
