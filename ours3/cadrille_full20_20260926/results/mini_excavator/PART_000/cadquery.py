import cadquery as cq
w0=cq.Workplane('YZ',origin=(1,0,0))
w1=cq.Workplane('YZ',origin=(7,0,0))
r=w0.sketch().segment((-60,-79),(1,-99)).segment((1,-98)).arc((94,-19),(35,86)).segment((36,87)).segment((-15,100)).segment((-16,98)).arc((-98,23),(-59,-73)).close().assemble().finalize().extrude(-98).union(w0.sketch().arc((-93,-34),(-86,-19),(-77,-7)).arc((-71,28),(-37,29)).arc((1,36),(36,29)).arc((58,28),(78,20)).arc((-35,93),(-93,-34)).assemble().finalize().extrude(-69)).union(w1.sketch().arc((-69,13),(68,-68),(-27,66)).arc((-63,52),(-69,13)).assemble().finalize().extrude(-106))