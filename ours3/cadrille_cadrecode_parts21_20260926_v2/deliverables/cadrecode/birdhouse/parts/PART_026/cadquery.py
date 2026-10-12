import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-14,12),(12,-14)).segment((14,-13)).segment((-9,15)).close().assemble().finalize().extrude(200)