import cadquery as cq
import cadquery as cq
w0=cq.Workplane('ZX',origin=(0,2,0))
r=w0.sketch().segment((-59,41),(-34,26)).segment((-57,2)).segment((-47,-7)).segment((-56,-7)).segment((-56,-27)).segment((-52,-27)).segment((-52,-99)).segment((-29,-99)).segment((-29,-100)).segment((-27,-100)).segment((-27,-99)).segment((11,-99)).segment((11,-87)).segment((59,-99)).segment((59,-73)).segment((49,-73)).segment((49,-65)).segment((55,-65)).segment((55,-41)).segment((49,-41)).segment((49,-26)).segment((34,-26)).segment((34,-14)).segment((44,-14)).segment((45,13)).segment((59,13)).segment((59,35)).segment((55,35)).segment((55,59)).segment((59,59)).segment((59,73)).segment((55,73)).segment((55,93)).segment((44,93)).segment((44,100)).segment((-52,100)).segment((-52,93)).segment((-57,93)).segment((-57,73)).segment((-52,73)).segment((-52,59)).segment((-57,59)).segment((-57,41)).close().assemble().push([(-10,-19)]).circle(32,mode='s').push([(-10,55)]).rect(32,10,mode='s').finalize().extrude(-4)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0047_00474878.step')
