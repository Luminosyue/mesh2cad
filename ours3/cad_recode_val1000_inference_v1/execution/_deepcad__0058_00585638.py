import cadquery as cq
import cadquery as cq
w0=cq.Workplane('XY',origin=(0,0,-13))
r=w0.sketch().segment((-93,38),(-93,39)).arc((-97,-25),(-60,-75)).segment((-60,-81)).segment((-52,-81)).arc((0,-100),(52,-83)).segment((60,-83)).segment((60,-78)).arc((74,-67),(86,-51)).segment((30,-76)).segment((25,-64)).arc((-19,-54),(-53,-20)).segment((-55,-20)).segment((-55,-16)).arc((-56,-12),(-56,-7)).segment((-59,-7)).segment((-59,-3)).segment((-56,-3)).arc((-56,0),(-55,3)).segment((-55,7)).segment((-53,7)).arc((-1,59),(60,25)).segment((60,26)).segment((91,26)).segment((89,50)).segment((85,50)).arc((49,87),(-3,99)).segment((-11,100)).segment((-11,99)).arc((-46,87),(-72,69)).segment((-64,69)).segment((-64,65)).arc((-55,73),(-44,79)).segment((-44,84)).segment((-69,74)).segment((-64,62)).segment((-64,61)).arc((-66,59),(-68,56)).segment((-68,38)).close().assemble().finalize().extrude(26)
compound=r.val()
cq.exporters.export(compound, '/data/home/cuiyuehan/project/mesh2cad/ours3/cad_recode_val1000_inference_v1/step/deepcad__0058_00585638.step')
