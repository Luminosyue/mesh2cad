import cadquery as cq
plane = cq.Plane(origin=[0.0008093276499840374, -0.35775674605354335, -0.40568849444389343], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(0.5222093398243465).extrude(0.8113769888877869)
