import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-31))
r=w0.sketch().arc((-95,31),(-81,-56),(1,-90)).arc((99,13),(-27,86)).arc((-41,84),(-55,79)).arc((-76,57),(-95,31)).assemble().finalize().extrude(47).union(w0.sketch().push([(10,-2)]).circle(80).circle(78,mode='s').finalize().extrude(61))