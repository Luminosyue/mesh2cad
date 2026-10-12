import cadquery as cq
plane = cq.Plane(origin=[-0.45555240696353305, 0.017721185090309233, -0.027629443711049893], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(np.float64(0.43965138289665706)).extrude(np.float64(0.8861944079399109))
