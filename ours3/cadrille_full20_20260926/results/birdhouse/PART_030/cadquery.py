import cadquery as cq
w0=cq.Workplane('YZ',origin=(-98,0,0))
w1=cq.Workplane('ZX',origin=(0,-96,0))
r=w0.sketch().segment((-92,-84),(-89,-87)).segment((-89,-84)).segment((-88,-84)).segment((-88,-88)).segment((-89,-88)).segment((-88,-89)).segment((-84,-93)).segment((-89,-96)).segment((-89,-97)).segment((-90,-97)).segment((-83,-100)).segment((-89,-84)).close().assemble().finalize().extrude(86).union(w0.sketch().segment((-100,-69),(-97,-75)).segment((-92,-72)).segment((-98,-66)).close().assemble().finalize().extrude(196)).union(w1.workplane(offset=33/2).moveTo(-90,87).cylinder(33,4))