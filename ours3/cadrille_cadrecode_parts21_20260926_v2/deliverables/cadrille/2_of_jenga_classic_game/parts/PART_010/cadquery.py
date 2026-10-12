import cadquery as cq
w0=cq.Workplane('YZ',origin=(96,0,0))
w1=cq.Workplane('XY',origin=(0,0,-76))
r=w0.sketch().segment((-97,38),(-95,-77)).segment((-85,-77)).segment((-85,-74)).segment((-79,-74)).segment((-79,-76)).segment((100,-74)).segment((96,40)).close().assemble().finalize().extrude(-193).union(w0.sketch().segment((-100,74),(-97,-71)).segment((98,-67)).segment((95,47)).close().assemble().finalize().extrude(-192)).union(w1.sketch().segment((31,-98),(96,-98)).segment((96,-24)).segment((31,-24)).segment((31,-31)).arc((33,-33),(31,-34)).close().assemble().finalize().extrude(153))