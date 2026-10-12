import cadquery as cq
plane = cq.Plane(origin=[-0.04100775346159935, 0.01983547387626891, -1.1963576755412264], xDir=[0.0, 0.0, -1.0], normal=[1.0, 0.0, 0.0])
result = cq.Workplane(plane).circle(1.2490032118752894).extrude(0.0820155069231987)
