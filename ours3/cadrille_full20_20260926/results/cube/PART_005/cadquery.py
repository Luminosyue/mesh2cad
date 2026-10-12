import cadquery as cq
w0=cq.Workplane('YZ',origin=(-94,0,0))
w1=cq.Workplane('YZ',origin=(-100,0,0))
r=w0.sketch().segment((-9,-92),(-6,-99)).segment((-3,-98)).segment((-5,-90)).close().assemble().finalize().extrude(184).union(w0.sketch().segment((-97,-97),(-97,-96)).segment((-95,-96)).segment((-95,-97)).arc((-95,-89),(-97,-97)).assemble().finalize().extrude(193)).union(w1.sketch().push([(-18,-96)]).circle(4).push([(-18,-96.5)]).rect(6,5,mode='s').finalize().extrude(6))