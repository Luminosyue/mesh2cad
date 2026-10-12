import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-100))
w1=cq.Workplane('XY',origin=(0,0,-25))
r=w0.sketch().arc((-82,-42),(22,-89),(83,10)).arc((82,12),(82,14)).arc((80,17),(79,20)).arc((76,22),(74,24)).arc((74,40),(72,57)).arc((-51,-71),(-10,91)).arc((-11,89),(-11,87)).arc((-77,44),(-82,-42)).assemble().finalize().extrude(129).union(w1.sketch().arc((-82,-42),(19,90),(29,-80)).segment((29,-74)).arc((80,-20),(48,45)).segment((48,51)).segment((43,51)).arc((0,60),(-43,51)).segment((-48,51)).segment((-48,45)).arc((-86,1),(-82,-42)).assemble().finalize().extrude(125))
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0041_00414996.step')
