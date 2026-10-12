import cadquery as cq
w0=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-100,-99),(-92,-99)).arc((-79,-98),(-66,-99)).segment((-57,-99)).arc((-59,-93),(-61,-87)).arc((-78,-96),(-97,-87)).arc((-99,-93),(-100,-99)).assemble().finalize().extrude(200)