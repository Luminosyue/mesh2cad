import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-2))
r=w0.sketch().segment((-100,-24),(-95,-24)).segment((-95,-39)).segment((-82,-39)).segment((-82,-24)).segment((-77,-24)).segment((-77,-21)).segment((-59,-21)).segment((-60,-43)).segment((-49,-43)).segment((-48,-21)).segment((-27,-21)).segment((-27,-43)).segment((20,-43)).segment((20,-24)).segment((25,-24)).segment((25,-16)).segment((43,-16)).segment((41,-43)).segment((77,-42)).segment((77,-36)).segment((100,-35)).segment((100,-14)).segment((87,-14)).segment((100,28)).segment((51,43)).segment((25,-14)).segment((25,-12)).segment((20,-12)).segment((20,1)).segment((10,1)).segment((10,17)).segment((8,17)).segment((8,43)).segment((-14,43)).segment((-14,35)).segment((-27,35)).segment((-27,17)).segment((-45,17)).segment((-45,1)).segment((-46,1)).segment((-46,17)).segment((-52,17)).segment((-52,43)).segment((-90,43)).segment((-79,17)).segment((-100,17)).close().assemble().push([(55,10)]).circle(14,mode='s').finalize().extrude(4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0026_00268139.step')
