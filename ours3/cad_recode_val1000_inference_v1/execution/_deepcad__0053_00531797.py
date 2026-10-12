import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-90))
r=w0.sketch().arc((-42,-32),(-10,-53),(27,-45)).segment((33,-42)).segment((32,-42)).arc((41,-34),(48,-24)).segment((40,-24)).segment((40,-17)).segment((41,-17)).arc((41,1),(33,17)).segment((33,42)).arc((-39,36),(-42,-32)).assemble().finalize().extrude(11).union(w0.sketch().arc((48,-6),(48,-3),(51,-5)).arc((45,5),(48,-6)).assemble().finalize().extrude(194)).union(w1.workplane(offset=184/2).moveTo(48,0).cylinder(184,5))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0053_00531797.step')
