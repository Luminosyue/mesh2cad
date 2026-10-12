import cadquery as cq
plane = cq.Plane(origin=[-0.05692005902528763, 0.10001416249335, 2.953841498271276], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(2.9919582374229132).workplane(offset=0.11384011805057526).circle(3.0152205498491536).loft(ruled=True)
