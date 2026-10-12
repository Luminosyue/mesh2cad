import cadquery as cq
import cadquery as cq
w0=cq.Workplane('YZ',origin=(30,0,0))
w1=cq.Workplane('XY',origin=(0,0,100))
r=w0.sketch().segment((-41,-100),(41,-100)).segment((41,-53)).arc((16,-70),(-13,-74)).segment((-13,-83)).segment((-23,-83)).segment((-23,-71)).arc((-35,-58),(-41,-42)).close().assemble().reset().face(w0.sketch().arc((-41,-36),(-35,-20),(-23,-8)).segment((-23,1)).segment((-13,1)).segment((-13,-8)).arc((16,-12),(35,-32)).segment((41,-32)).segment((41,91)).segment((-41,91)).close().assemble()).finalize().extrude(-60).union(w0.workplane(offset=10/2).moveTo(0,-33).cylinder(10,16)).union(w1.sketch().segment((-40,-41),(40,-41)).segment((40,41)).segment((30,41)).segment((30,6)).segment((-40,6)).close().assemble().finalize().extrude(-194))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__21899_d55d6c08_0028.step')
