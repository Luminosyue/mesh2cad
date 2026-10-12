import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,9,0))
r=w0.sketch().segment((-16,-66),(-12,-66)).arc((15,-94),(46,-66)).segment((47,-66)).segment((47,-53)).segment((46,-53)).arc((15,-32),(-12,-53)).segment((-16,-53)).close().assemble().finalize().extrude(-18).union(w0.sketch().arc((-8,77),(1,65),(13,58)).segment((13,52)).arc((22,58),(29,66)).segment((30,66)).segment((30,60)).arc((36,65),(33,72)).arc((22,99),(-5,84)).segment((-6,84)).segment((-6,77)).close().assemble().finalize().extrude(-11)).union(w0.sketch().segment((-47,-84),(-40,-84)).segment((-40,-100)).segment((17,-100)).segment((17,-84)).segment((24,-84)).segment((24,-24)).segment((17,-24)).segment((17,-23)).segment((-1,-23)).segment((-1,2)).segment((16,2)).segment((16,34)).segment((-12,34)).segment((-12,29)).segment((-47,29)).close().assemble().push([(-11,-59)]).circle(1,mode='s').finalize().extrude(-7))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0011_00110690.step')
