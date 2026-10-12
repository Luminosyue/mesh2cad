import cadquery as cq
w0=cq.Workplane('YZ',origin=(91,0,0))
w1=cq.Workplane('XY',origin=(0,0,-99))
r=w0.sketch().segment((-98,15),(-95,-100)).segment((98,-97)).segment((95,17)).close().assemble().finalize().extrude(-189).union(w0.sketch().segment((-99,53),(-97,-99)).segment((99,-97)).segment((97,56)).close().assemble().finalize().extrude(-189)).union(w1.sketch().push([(-18,0)]).circle(100).circle(72,mode='s').finalize().extrude(83))