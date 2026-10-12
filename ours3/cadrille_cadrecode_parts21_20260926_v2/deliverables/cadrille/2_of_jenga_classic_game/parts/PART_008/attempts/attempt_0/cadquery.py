import cadquery as cq
w0=cq.Workplane('YZ',origin=(98,0,0))
w1=cq.Workplane('YZ',origin=(100,0,0))
r=w0.sketch().segment((-99,-21),(97,-21)).segment((97,21)).segment((93,21)).arc((83,19),(73,21)).segment((-99,21)).close().assemble().push([(-35,18)]).circle(3,mode='s').finalize().extrude(-197).union(w1.sketch().segment((-91,-21),(91,-21)).segment((91,21)).segment((-91,21)).segment((-91,12)).arc((-88,10),(-91,8)).close().assemble().finalize().extrude(-198))