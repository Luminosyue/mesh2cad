# FULL20 自动接续队列

2026-09-25，依据用户指令“跑完这几个case卡空出来继续跑剩下的”，已启动持久后台调度器。

- 调度器 PID：4072862。
- 使用 GPU 0、1、3、4、5、6；保留 GPU 2 给现有 Tank 及修补组流程，排除 GPU 7。
- 等现有训练进程及其自由生成结束、显存释放，并连续两次确认容量后接续。检查周期 20 秒。
- 当前第一项：DVD player，GPU 4，PID 4116790；其后为 speaker、robot、pressure cooker、airplane、Jenga、toaster、birdhouse、mini fire engine、vegetable set、sofa、winerack。
- 保留现有训练进程、产物和 checkpoint；已有尝试不自动重跑。失败记录后继续其他对象。
- 检查数据及标签哈希。沿用模型训练 v2 快照，q14 + Compact IR V3、完整序列、空目标贪心生成和 natural EOS。冻结 Tank PART_029 不进入此队列。
- `/data` 至少保留 15 GB，checkpoint 所在磁盘保留 30 GB 并为运行中的训练额外预留空间；不足时暂停新启动，不自动删文件。
- 新对象自由生成完成后，串行执行现有 CAD/BRep、STEP 和几何验证；同时补上奶泡机的 CAD 验证。

## 完整性口径

剩余 12 个对象当前均只有部分零件可训练，原始对象身份与完整零件清单不变。自动接续并不解决全部缺件或坏标签。可用部分自由生成通过不能算完整对象成功，CAD gate 仍要求原清单全部零件。

| 对象 | 当前训练零件 / 原清单 |
|---|---:|
| dvd_player | 6 / 7 |
| speaker_big | 10 / 12 |
| robot | 15 / 17 |
| pressure_cooker | 11 / 13 |
| airplane | 5 / 9 |
| 2_of_jenga_classic_game | 11 / 13 |
| toaster | 37 / 39 |
| birdhouse | 30 / 36 |
| mini_fire_engine | 7 / 16 |
| assorted_vegetable_set | 5 / 11 |
| 3d_dollhouse_sofa | 3 / 8 |
| winerack | 4 / 34 |

## 服务器审计位置

项目目录：`/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1`

- `model_v1/autoqueue_side_20260925/MANIFEST.json`：授权、固定队列、逐对象阻塞清单、数据与脚本哈希。
- `model_v1/autoqueue_side_20260925/STATE.json`：实时队列与磁盘状态。
- `model_v1/autoqueue_side_20260925/events.jsonl`：启动、退出和错误事件。
- `model_v1/autoqueue_side_20260925/claims/`：每对象唯一启动记录。
- `model_v1/logs/continue_full20_side.log`：后台调度日志。
- `model_v1/runs/<object>/`：实际训练与自由生成证据。
- `model_v1/generated/<object>/free_<step>/OBJECT_GATE.json`：独立 CAD 完整性判定。

此队列没有接管现有 Tank 修补启动器，也不据其存在推断修补模型训练已启动。输入仍为预分割 X-Part mesh 采样；编译依赖每零件模板和量化元数据。这是训练对象记忆验证，不是未见对象泛化。
