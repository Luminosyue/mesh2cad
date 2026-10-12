# TANK_FULL_OBJECT_Q14_V3_AUDIT_AND_ASSEMBLY_V1

- Actual Tank parts: **45**; historical 45 matches scan.
- Q14: **45/45** existing canonical CadQuery STEP. Compact IR V3: **1/45** explicitly available in the frozen strict artifact (`PART_029`); no missing CAD parts.
- `PART_029`: reused unchanged from frozen Demo5 result; q-stream 1529/1529 exact, natural EOS PASS, BRep PASS, STEP readback PASS, volume error 0.0. No re-quantization or retraining.
- Strict model-generated parts: **1/45**. Assembly: **MIXED_ASSEMBLY**, not fully model-generated.
- Object-coordinate gate: **PASS (45/45 transform records)**; assembly coverage **45/45**.
- `TANK_FULL_CAD_ASSEMBLY_PASS=TRUE`; `TANK_FULL_MODEL_GENERATION_PASS=FALSE`.
- Full-object CD/IoU are not claimed because source OBJ is not asserted watertight and no new non-comparable sampling protocol was introduced.
