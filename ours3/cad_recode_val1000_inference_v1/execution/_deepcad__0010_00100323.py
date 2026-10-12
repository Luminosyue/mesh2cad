import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-72))
w1=cq.Workplane('XY',origin=(0,0,-62))
r=w0.sketch().segment((-84,-42),(-67,-42)).segment((-67,-53)).segment((-10,-53)).segment((-10,-42)).segment((1,-42)).segment((1,-39)).segment((30,-39)).segment((30,-32)).segment((1,-32)).segment((1,-13)).segment((-40,-13)).segment((-40,53)).segment((-84,53)).close().assemble().finalize().extrude(36).union(w0.sketch().push([(-70,-12)]).circle(30).circle(29,mode='s').push([(70,-12)]).circle(30).finalize().extrude(144)).union(w1.sketch().arc((42,-19),(43,-22),(43,-24)).arc((100,-13),(42,-19)).assemble().finalize().extrude(116))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0010_00100323.step')
