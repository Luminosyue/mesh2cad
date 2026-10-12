import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-21),(-98,-25)).segment((-69,-11)).segment((-69,-13)).segment((-50,-13)).segment((-50,-2)).segment((-49,-1)).segment((-17,-1)).segment((-17,-13)).segment((-21,-13)).segment((-21,-14)).segment((-17,-14)).segment((-17,-19)).segment((-1,-24)).arc((10,-27),(21,-25)).segment((22,-25)).segment((22,-24)).arc((24,-22),(26,-20)).arc((58,-32),(88,-19)).segment((88,-22)).segment((91,-22)).segment((91,-17)).arc((100,0),(91,18)).segment((91,22)).segment((88,22)).segment((88,18)).arc((81,21),(74,22)).arc((64,32),(52,25)).arc((46,22),(41,18)).segment((40,18)).segment((40,17)).arc((36,12),(33,6)).arc((14,0),(2,-13)).segment((1,-13)).segment((1,-11)).arc((-1,-6),(-2,0)).segment((-49,-1)).segment((-49,-2)).segment((-50,-2)).segment((-50,-3)).segment((-87,-14)).segment((-88,-14)).close().assemble().push([(67,0)]).circle(17,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/fusion360__60760_f95d00ad_0024.step')
