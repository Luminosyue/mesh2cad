# FULL20 FINAL COMPLETION STATUS

Updated: 2026-09-25 15:59:14 +0800

FULL_MODEL_ASSEMBLY_PASS = 10/20
CURRENT_PARTIAL_N = 8
CURRENT_BLOCKED_N = 1
CURRENT_TRAINING_N = 3

DONE:
- robot
- android_figure_orange
- pottery_large
- fire_truck
- pressure_cooker
- speaker_big
- dvd_player
- cube
- baby_car
- aroma_stainless_steel_milk_frother_2_cup

PARTIAL:
- tank | 1/45 free | 1/45 CAD/STEP | remaining 44
- airplane | 5/9 free | 5/9 CAD/STEP | remaining 4
- 3d_dollhouse_sofa | 3/8 free | 3/8 CAD/STEP | remaining 5
- winerack | 2/34 free | 2/34 CAD/STEP | remaining 32
- mini_fire_engine | 7/16 free | 7/16 CAD/STEP | remaining 9
- mini_excavator | 5/10 free | 5/10 CAD/STEP | remaining 5
- 2_of_jenga_classic_game | 3/13 free | 3/13 CAD/STEP | remaining 10
- assorted_vegetable_set | 4/11 free | 4/11 CAD/STEP | remaining 7

ACTIVE WORKERS:
- PID 770311 GPU 1 | /data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python -u /var/tmp/cuiyuehan_full20_completion_20260925/train_part_completion.py mini_excavator__PART_002__PARALLEL_1790322903
- PID 770313 GPU 2 | /data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python -u /var/tmp/cuiyuehan_full20_completion_20260925/train_part_completion.py mini_excavator__PART_008__PARALLEL_1790322903
- PID 770314 GPU 3 | /data/home/cuiyuehan/.conda/envs/mesh2cad_formal_v1/bin/python -u /var/tmp/cuiyuehan_full20_completion_20260925/train_part_completion.py mini_excavator__PART_009__PARALLEL_1790322903

BLOCKER CLASS COUNTS:
- B. FREE_GENERATION_BLOCKER: 2
- G. CAD_BREP_BLOCKER: 14
- K. MISSING_INPUT: 49
- L. UNKNOWN: 5

DISK_FREE_GB = 156.3

GPU SNAPSHOT:
```
0, 555, 45035, 0
1, 26715, 18875, 98
2, 26715, 18875, 98
3, 26715, 18875, 98
4, 3199, 42391, 0
5, 4, 45586, 0
6, 4, 45586, 0
7, 699, 44891, 7
```

Representation: q14 + Compact IR V3; canonical controls are not model success; texture reconstruction is out of scope.

Remaining blocker detail is in tables/FINAL_REMAINING_PART_BLOCKERS.csv.
