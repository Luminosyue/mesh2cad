import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,1,0))
r=w0.sketch().segment((-82,-20),(-23,-51)).segment((-23,-61)).segment((-17,-61)).segment((-17,-56)).segment((-15,-57)).segment((-11,-49)).segment((-17,-45)).segment((-17,-37)).segment((-33,-37)).segment((-79,-17)).close().assemble().reset().face(w0.sketch().segment((-69,65),(-66,56)).segment((-37,61)).segment((-37,56)).segment((-36,56)).segment((-36,29)).segment((-17,29)).segment((-17,35)).segment((-15,36)).segment((-18,45)).segment((-18,68)).segment((-36,68)).segment((-36,62)).segment((-37,62)).segment((-37,67)).segment((-39,68)).segment((-57,68)).segment((-57,69)).close().assemble()).reset().face(w0.sketch().segment((17,99),(24,99)).segment((24,88)).segment((56,88)).segment((56,40)).segment((68,36)).segment((68,85)).segment((64,85)).segment((64,100)).segment((17,100)).close().assemble()).push([(39,-94)]).circle(6).push([(50,-29)]).circle(12).push([(75,-86.5)]).rect(14,9).finalize().extrude(-3)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0069_00693757.step')
