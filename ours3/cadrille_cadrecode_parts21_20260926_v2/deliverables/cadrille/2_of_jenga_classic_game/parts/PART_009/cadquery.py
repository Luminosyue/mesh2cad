import cadquery as cq
w0=cq.Workplane('YZ',origin=(98,0,0))
w1=cq.Workplane('XY',origin=(0,0,21))
r=w0.sketch().segment((-100,-21),(99,-21)).segment((99,18)).segment((-99,21)).close().assemble().finalize().extrude(-196).union(w1.sketch().segment((-97,-98),(97,-98)).segment((97,98)).segment((-97,98)).segment((-97,86)).arc((-93,67),(-97,48)).close().assemble().push([(35,60)]).circle(3,mode='s').finalize().extrude(-42))