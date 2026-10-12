# GT_EXEC_AUDIT

GT 未修改。executor = `cad_execution_failure_audit.staged_execute`.

| group | n | PARSE | EXEC | STEP_WRITE | STEP_RELOAD | GEOMETRY |
|---|---:|---:|---:|---:|---:|---:|
| overall | 800 | 800 | 800 | 730 | 730 | 640/800 |
| deepcad | 640 | 640 | 640 | 598 | 598 | 640/640 |
| fusion360 | 160 | 160 | 160 | 132 | 132 | 0/160 |

Fusion360 的 `GT_GEOMETRY_PASS=0/160` 来自 stage1 `label_gate` 字段：该文件里 Fusion360 的 label_gate 全是 false（DeepCAD 专用门）。V3 入选 Fusion360 用的是另一份 `STRICT_LABEL_PASS`。直播 `staged_execute`：Fusion360 parse/exec 160/160，STEP 132/160。

70 条 STEP_WRITE 失败原因都是 `BREP_INVALID`（OCC 形状无效，未改 GT）。


failures = 70

| cad_id | source | stage | exception |
|---|---|---|---|
| deepcad__0001_00017084 | deepcad | STEP_WRITE | `None` |
| deepcad__0004_00041299 | deepcad | STEP_WRITE | `None` |
| deepcad__0007_00079994 | deepcad | STEP_WRITE | `None` |
| deepcad__0008_00084890 | deepcad | STEP_WRITE | `None` |
| deepcad__0013_00131797 | deepcad | STEP_WRITE | `None` |
| deepcad__0014_00146755 | deepcad | STEP_WRITE | `None` |
| deepcad__0015_00157698 | deepcad | STEP_WRITE | `None` |
| deepcad__0017_00179955 | deepcad | STEP_WRITE | `None` |
| deepcad__0022_00222961 | deepcad | STEP_WRITE | `None` |
| deepcad__0027_00278233 | deepcad | STEP_WRITE | `None` |
| deepcad__0031_00318631 | deepcad | STEP_WRITE | `None` |
| deepcad__0033_00335922 | deepcad | STEP_WRITE | `None` |
| deepcad__0033_00337831 | deepcad | STEP_WRITE | `None` |
| deepcad__0034_00345680 | deepcad | STEP_WRITE | `None` |
| deepcad__0038_00385667 | deepcad | STEP_WRITE | `None` |
| deepcad__0039_00398180 | deepcad | STEP_WRITE | `None` |
| deepcad__0042_00421864 | deepcad | STEP_WRITE | `None` |
| deepcad__0045_00453534 | deepcad | STEP_WRITE | `None` |
| deepcad__0045_00457381 | deepcad | STEP_WRITE | `None` |
| deepcad__0046_00461912 | deepcad | STEP_WRITE | `None` |
| deepcad__0046_00466875 | deepcad | STEP_WRITE | `None` |
| deepcad__0046_00469414 | deepcad | STEP_WRITE | `None` |
| deepcad__0048_00487478 | deepcad | STEP_WRITE | `None` |
| deepcad__0053_00532997 | deepcad | STEP_WRITE | `None` |
| deepcad__0054_00540800 | deepcad | STEP_WRITE | `None` |
| deepcad__0055_00552822 | deepcad | STEP_WRITE | `None` |
| deepcad__0057_00570901 | deepcad | STEP_WRITE | `None` |
| deepcad__0058_00587657 | deepcad | STEP_WRITE | `None` |
| deepcad__0059_00598231 | deepcad | STEP_WRITE | `None` |
| deepcad__0060_00605561 | deepcad | STEP_WRITE | `None` |
| deepcad__0062_00629385 | deepcad | STEP_WRITE | `None` |
| deepcad__0063_00630498 | deepcad | STEP_WRITE | `None` |
| deepcad__0063_00639931 | deepcad | STEP_WRITE | `None` |
| deepcad__0068_00687884 | deepcad | STEP_WRITE | `None` |
| deepcad__0070_00703787 | deepcad | STEP_WRITE | `None` |
| deepcad__0073_00735284 | deepcad | STEP_WRITE | `None` |
| deepcad__0079_00791303 | deepcad | STEP_WRITE | `None` |
| deepcad__0079_00796453 | deepcad | STEP_WRITE | `None` |
| deepcad__0084_00845177 | deepcad | STEP_WRITE | `None` |
| deepcad__0087_00873370 | deepcad | STEP_WRITE | `None` |
| deepcad__0093_00934864 | deepcad | STEP_WRITE | `None` |
| deepcad__0098_00987776 | deepcad | STEP_WRITE | `None` |
| fusion360__111501_1e74ed05_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__118124_46a97d36_0003 | fusion360 | STEP_WRITE | `None` |
| fusion360__122515_758d8b70_0004 | fusion360 | STEP_WRITE | `None` |
| fusion360__128281_be786720_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__130757_b2c47f8d_0004 | fusion360 | STEP_WRITE | `None` |
| fusion360__138161_8fa1cb24_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__21497_9833a679_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__24133_2ac9dc04_0005 | fusion360 | STEP_WRITE | `None` |
| fusion360__24230_636208ab_0005 | fusion360 | STEP_WRITE | `None` |
| fusion360__24927_543d2801_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__30400_8824ce97_0007 | fusion360 | STEP_WRITE | `None` |
| fusion360__30426_2cde26de_0002 | fusion360 | STEP_WRITE | `None` |
| fusion360__33147_d7173b68_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__34521_49e7972b_0003 | fusion360 | STEP_WRITE | `None` |
| fusion360__38260_2a31c6df_0015 | fusion360 | STEP_WRITE | `None` |
| fusion360__38288_740bfe5a_0007 | fusion360 | STEP_WRITE | `None` |
| fusion360__40624_e1c5c424_0001 | fusion360 | STEP_WRITE | `None` |
| fusion360__41234_74275eb0_0001 | fusion360 | STEP_WRITE | `None` |
| fusion360__41859_173a686e_0003 | fusion360 | STEP_WRITE | `None` |
| fusion360__45680_5b1610e8_0007 | fusion360 | STEP_WRITE | `None` |
| fusion360__50777_2934de55_0020 | fusion360 | STEP_WRITE | `None` |
| fusion360__53470_39f2e9dc_0005 | fusion360 | STEP_WRITE | `None` |
| fusion360__57738_4610041b_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__60739_f118b838_0001 | fusion360 | STEP_WRITE | `None` |
| fusion360__61007_ea617ece_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__61379_d9f89cb9_0001 | fusion360 | STEP_WRITE | `None` |
| fusion360__83112_fbb40a06_0000 | fusion360 | STEP_WRITE | `None` |
| fusion360__83210_07c13a64_0000 | fusion360 | STEP_WRITE | `None` |
