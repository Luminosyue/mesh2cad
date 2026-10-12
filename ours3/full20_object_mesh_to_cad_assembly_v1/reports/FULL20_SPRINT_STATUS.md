# FULL20 Sprint Status

Updated: 2026-09-26 15:32:47 +0800

FULL_MODEL_ASSEMBLY_PASS = 19/20

TARGET_SCOPE = 20 non-Airplane cases; Paintmaker substitutes for Airplane

DONE =
- Milk Frother
- Pottery Large
- Jenga
- Sofa
- Android Figure
- Vegetable Set
- Baby Car
- Birdhouse
- Cube
- DVD Player
- Fire Truck
- Mini Excavator
- Mini Fire Engine
- Paintmaker
- Pressure Cooker
- Robot
- Speaker Big
- Toaster
- Winerack

NEAR_COMPLETE =
- Android Figure 5/5 | REPAIRED | FULL_OBJECT_PASS
- Cube 7/7 | REPAIRED | FULL_OBJECT_PASS
- Baby Car 7/7 | REPAIRED | FULL_OBJECT_PASS
- Pressure Cooker 13/13 | REPAIRED | FULL_OBJECT_PASS
- Speaker Big 12/12 | REPAIRED | FULL_OBJECT_PASS

ACTIVE_TRAINING =
- Global dynamic queue: 130 completed, 0 running, 0 pending, 0 failed
- Tank update 640
- Mini Fire Engine update 480
- Birdhouse update 800 | trajectory 320:28891, 360:24540, 480:17560, 640:9211, 800:5115 | plateau NO
- Assorted Vegetable Set update 640

BLOCKERS =
- Pending full-object gates: Tank
- Tank unresolved strict labels: 0
- Airplane: excluded by request

GPU3 =
- IDLE

PAPER_MAIN_4_OBJECT_DEMO_READY = YES
Demo path = /data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/paper_demo/PAPER_MAIN_4_OBJECT_DEMO.png

Success count uses only `model_v1/generated/*/*/OBJECT_GATE.json` files with `FULL_MODEL_ASSEMBLY_PASS=true`. Geometry metrics remain separate from pipeline success.
