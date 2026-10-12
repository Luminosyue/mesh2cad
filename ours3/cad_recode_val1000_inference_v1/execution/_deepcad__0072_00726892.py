import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,-100,0))
w1=cq.Workplane('ZX',origin=(0,-57,0))
r=w0.sketch().arc((-29,-7),(-24,-1),(-21,5)).arc((-20,13),(-12,20)).arc((5,24),(18,15)).arc((23,10),(26,4)).arc((27,1),(28,-2)).arc((29,-5),(29,-8)).arc((28,-10),(28,-11)).arc((24,-17),(18,-21)).arc((15,-24),(11,-26)).arc((10,-25),(8,-22)).arc((-10,-22),(-21,-10)).arc((-25,-7),(-29,-2)).close().assemble().finalize().extrude(192).union(w0.sketch().arc((-29,-7),(1,-30),(29,-5)).arc((21,11),(23,29)).arc((1,30),(-18,22)).segment((-18,16)).segment((-26,16)).arc((-29,4),(-29,-7)).assemble().push([(0,-1)]).circle(23,mode='s').finalize().extrude(200)).union(w1.sketch().arc((-20,-13),(-16,-17),(-10,-20)).segment((-10,-23)).segment((10,-23)).segment((10,-20)).arc((16,-17),(20,-13)).close().assemble().finalize().extrude(149))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0072_00726892.step')
