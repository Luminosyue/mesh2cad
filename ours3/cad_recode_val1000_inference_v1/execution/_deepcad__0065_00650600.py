import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,0))
r=w0.sketch().segment((-100,2),(-87,-20)).segment((-78,-15)).segment((-78,-25)).segment((71,-25)).segment((71,-2)).segment((100,-2)).segment((100,7)).segment((99,7)).arc((95,17),(89,25)).segment((71,25)).segment((71,20)).segment((-52,20)).segment((-52,25)).segment((-62,25)).segment((-62,15)).segment((-63,17)).close().assemble().push([(25,-5)]).circle(17,mode='s').finalize().extrude(-10).union(w0.sketch().segment((44,18),(54,18)).segment((54,-2)).segment((50,-2)).segment((50,-11)).segment((54,-11)).segment((54,-20)).segment((96,-20)).segment((96,-11)).segment((91,-11)).segment((91,-2)).segment((96,-2)).segment((96,18)).segment((98,18)).segment((98,20)).segment((89,20)).segment((89,25)).segment((54,25)).segment((54,20)).segment((44,20)).close().assemble().finalize().extrude(10))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0065_00650600.step')
