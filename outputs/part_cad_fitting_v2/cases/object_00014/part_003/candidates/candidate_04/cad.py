import cadquery as cq
plane = cq.Plane(origin=[0.001376410447941359, -0.32508984208106995, -0.0026203790160778373], xDir=[0.0, 0.0, 1.0], normal=[0.0, 1.0, 0.0])
result = cq.Workplane(plane).circle(0.49152742665342863).extrude(0.6501796841621399)
