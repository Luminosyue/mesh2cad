import cadquery as cq
w0=cq.Workplane('YZ',origin=(-27,0,0))
w1=cq.Workplane('XY',origin=(0,0,-89))
r=w0.workplane(offset=-93/2).moveTo(-74,-92).cylinder(93,4).union(w0.sketch().segment((-99,-94),(-61,-100)).segment((-56,-89)).segment((-94,-89)).close().assemble().finalize().extrude(-10)).union(w1.sketch().arc((51,-96),(61,-96),(70,-93)).segment((89,-93)).segment((89,-96)).segment((95,-96)).arc((98,-92),(100,-90)).arc((98,-88),(97,-85)).arc((94,-54),(93,-85)).arc((92,-88),(91,-91)).segment((89,-91)).segment((89,-94)).segment((70,-94)).arc((61,-97),(51,-96)).assemble().finalize().extrude(-7))