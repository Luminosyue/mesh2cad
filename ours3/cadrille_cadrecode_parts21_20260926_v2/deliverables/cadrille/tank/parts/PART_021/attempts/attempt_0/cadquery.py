import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-17))
w1=cq.Workplane('YZ',origin=(62,0,0))
r=w0.sketch().push([(-5,82)]).circle(18).circle(12,mode='s').finalize().extrude(-16).union(w0.sketch().arc((-49,67),(-88,-37),(10,-99)).segment((10,-97)).segment((13,-97)).segment((13,-98)).arc((91,2),(-18,82)).arc((-33,73),(-49,67)).assemble().push([(0,-12)]).circle(70,mode='s').finalize().extrude(50)).union(w1.sketch().arc((-78,-16),(-16,-15),(43,-16)).arc((95,-21),(54,11)).arc((-20,22),(-78,-16)).assemble().push([(71,-10)]).circle(22,mode='s').finalize().extrude(-110))