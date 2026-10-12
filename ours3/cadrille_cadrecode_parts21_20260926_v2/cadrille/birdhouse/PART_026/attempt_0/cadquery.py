import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-13,12),(12,-14)).segment((13,-13)).segment((-9,14)).close().assemble().finalize().extrude(200)