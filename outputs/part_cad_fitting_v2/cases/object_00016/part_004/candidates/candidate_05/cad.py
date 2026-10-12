import cadquery as cq
plane = cq.Plane(origin=[0.009619437548553923, -5.744169414097776, -0.40568849444389343], xDir=[0.0, -1.0, 0.0], normal=[0.0, 0.0, 1.0])
result = cq.Workplane(plane).circle(5.8511632385878585).workplane(offset=0.8113769888877869).circle(5.8515970241397035).loft(ruled=True)
