import cadquery as cq
w0=cq.Workplane('YZ',origin=(-77,0,0))
w1=cq.Workplane('XY',origin=(0,0,92))
r=w0.sketch().segment((-20,-99),(17,-100)).segment((18,-73)).arc((0,-75),(-19,-71)).close().assemble().reset().face(w0.sketch().arc((-18,84),(0,84),(19,80)).segment((20,99)).segment((-17,100)).close().assemble()).push([(16.5,-11.5)]).rect(3,157).finalize().extrude(154).union(w1.sketch().segment((-73,-21),(-72,-21)).arc((-71,-19),(-70,-21)).segment((72,-21)).segment((72,21)).segment((-73,21)).close().assemble().finalize().extrude(-185))