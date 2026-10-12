import cadquery as cq
plane = cq.Plane(origin=[-0.0068802746891800815, 0.037866046951079646, -0.33748385310173035], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.49137059587379267).workplane(offset=0.6749677062034607).circle(0.3727216218388166).loft(ruled=True)
