# FULL20 / Tank：P1 模型训练与自由生成执行记录

更新时间：2026-09-25T11:39:44+08:00

已按最新指令启动真实 P1 专项 full-sequence overfit。旧 canonical 批处理结果仅作为训练标签、数据准备和对照。当前 FULL20_MODEL_GENERATION_PASS = FALSE，已通过完整模型装配验收的对象为 1/20。

## 实际训练配置

- 起点 checkpoint：`/data/home/cuiyuehan/project/mesh2cad/ours3/p3_xpart_v3_optimizer_memory_demo5_v1/frozen_tf5_success_v1`。
- 已追溯链路：P1v2 checkpoint-6000 → Airplane PART000 → Airplane3 → Airplane9 → V3 demo5 frozen step160 → 本轮。
- 每对象专项 overfit，使用 1,238,440,960 个可训练参数；点云编码器冻结，语言模型/投影层 AdamW 更新。
- q14 + Compact IR V3 未修改。Tank context=65536，其余优先对象 context=32768；逐样本核对完整监督目标与标签一致，禁止截断、分块目标和 GT 文本前缀。
- 输入：原始 X-Part mesh 的 2048 个确定性表面采样点，使用共同 object frame；后三个通道为零。本轮不加载 curve registry。
- 这是已见训练对象的记忆验证，不是未见对象泛化；需要预分割 X-Part 输入。V3 仍依赖逐零件语义模板、编译程序结构和量化元数据。
- 新 checkpoint 存储：`/var/tmp/cuiyuehan_full20_p1_v3_20260925`，位于独立系统盘；实验目录 `model_v1/checkpoints` 为对应链接。
- 每对象初始20步保存 checkpoint；既定 TF 检查通过后进行完整自由生成，最多640步。320步后 LR 从5e-6降为2e-6。无优化器状态副本。

## 当前实际进度

| 对象 | 应有 parts | 当前训练步 | 新 checkpoint | 阻塞零件数 |
|---|---:|---:|---|---:|
| tank | 45 | 133 | /var/tmp/cuiyuehan_full20_p1_v3_20260925/tank/checkpoint-20-initial | 12 |
| android_figure_orange | 5 | 384 | /var/tmp/cuiyuehan_full20_p1_v3_20260925/android_figure_orange/checkpoint-20-initial | 0 |
| pottery_large | 3 | 320 | /var/tmp/cuiyuehan_full20_p1_v3_20260925/pottery_large/checkpoint-320-free_eval | 0 |
| fire_truck | 8 | 90 | /var/tmp/cuiyuehan_full20_p1_v3_20260925/fire_truck/checkpoint-20-initial | 0 |
| mini_excavator | 10 | 排队 | 尚未保存 | 0 |
| cube | 7 | 128 | /var/tmp/cuiyuehan_full20_p1_v3_20260925/cube/checkpoint-20-initial | 0 |
| baby_car | 7 | 182 | /var/tmp/cuiyuehan_full20_p1_v3_20260925/baby_car/checkpoint-20-initial | 0 |

pottery_large 当前自由生成已落盘：3 个 exact，3 个 natural EOS；全对象 CAD 验收状态另见 JSON。

已验收完整模型对象：pottery_large，全部 3 个零件；checkpoint `/var/tmp/cuiyuehan_full20_p1_v3_20260925/pottery_large/checkpoint-320-free_eval`。
实测 mesh-vs-generated-CAD：CD=0.008020925，surface IoU64=0.579513557，体积相对误差=0.20747472703550102。
视觉核对：整体杯状结构和全部零件保留，但原网格表面纹理未重建；体积误差约20.75%。free exact 表示精确记忆已有标签，不能据此宣称原mesh精确重建。
完整 STEP：`/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/model_v1/generated/pottery_large/free_320/assembled.step`。预览：`model_v1/paper_demo/POTTERY_LARGE_MODEL_DEMO.png`。

首批6个完整对象：Pottery Large、Android Figure Orange、Cube、Baby Car、Fire Truck、Mini Excavator，共40个零件；GPU 1 顺序执行。Tank 的32个已验证零件在 GPU 2 同时训练。

## 成功口径与自动验收

1. 生成时去除所有监督目标 token，只保留用户提示与输入点云；greedy、num_beams=1，不给 GT 前缀。
2. 自然 EOS 和整个输出 token 序列（含长度）的精确匹配分别记录。64-token 推理冒烟测试仅证明执行路径可运行，不计作完整生成成功。
3. 实际解析生成 V3，验证 op/feature header 和 q14 范围，将生成的 q 值写入声明的模板后执行 CAD。不得用 canonical q 值替代。
4. 检查 BRep、STEP 导出/读回及原坐标；完整 part 集全部通过后构造 multi-body compound，不做布尔合并或 ICP。
5. 实际采样比较输入 mesh 与生成 CAD。CD 沿用项目统一 surface sampling；IoU 明确为既有 surface voxel IoU64，不是实心体积 IoU，也不是 text-exact 后赋值1/0。
6. 每个完整对象成功后保存 STEP、几何指标和6张1600×1200渲染；只有 `generated/<object>/free_<step>/OBJECT_GATE.json` 的 `FULL_MODEL_ASSEMBLY_PASS=true` 才计为完整模型对象成功。

## 必须保留的阻塞与审计

- 冻结的20个对象实际需要304个零件，不是早期误统计的254个。254是已有 X-Part 数，50个输入缺失；最初计数错误及失效的部分 Winerack 演示已保留审计，未替换对象。
- 221个 canonical 零件通过现有链路，其中 Tank PART_029 为历史冻结成功；本轮可训练220个。另有19个 BRep失败、14个几何一致性失败、50个输入缺失。
- 旧7个完整 canonical 装配不计入新的模型成功数。
- Tank 应有45个零件：32个开始本轮训练，PART_029仅复用历史冻结结果，12个标签阻塞。不能因此宣称完整 Tank 成功。
- Tank 阻塞：PART_004, PART_010, PART_012, PART_013, PART_015, PART_017, PART_019, PART_024, PART_025, PART_027, PART_037, PART_044。其中10个 Q14_BREP_INVALID，PART_024和PART_027为几何一致性失败；已达到原批处理每零件最多3次修复限制，失败记录全部保留。
- Tank PART_029 未训练、未重新生成；其原始IR、q元数据和STEP哈希均保持不变。

## 冻结对象清单

| Object | 应有 parts | 当前被阻塞的标签或输入 |
|---|---:|---:|
| tank | 45 | 12 |
| airplane | 9 | 4 |
| robot | 17 | 2 |
| toaster | 39 | 2 |
| android_figure_orange | 5 | 0 |
| 3d_dollhouse_sofa | 8 | 5 |
| winerack | 34 | 30 |
| pottery_large | 3 | 0 |
| mini_fire_engine | 16 | 9 |
| fire_truck | 8 | 0 |
| mini_excavator | 10 | 0 |
| pressure_cooker | 13 | 2 |
| speaker_big | 12 | 2 |
| dvd_player | 7 | 1 |
| cube | 7 | 0 |
| 2_of_jenga_classic_game | 13 | 2 |
| assorted_vegetable_set | 11 | 6 |
| baby_car | 7 | 0 |
| birdhouse | 36 | 6 |
| aroma_stainless_steel_milk_frother_2_cup | 4 | 0 |

## 关键路径

项目根：`/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1`
当前模型实验：`/data/home/cuiyuehan/project/mesh2cad/ours3/full20_object_mesh_to_cad_assembly_v1/model_v1`

- 原始冻结清单：`manifests/FULL20_OBJECT_MANIFEST.csv`
- 原 canonical 对象/零件表：`tables/FULL20_OBJECT_RESULTS.csv`、`tables/FULL20_ALL_PART_RESULTS.csv`
- 新模型实时表：`model_v1/tables/FULL20_OBJECT_MODEL_RESULTS.csv`
- 新模型实时状态：`model_v1/reports/MODEL_LIVE_STATUS.json`、`reports/PROGRESS.md`
- 新模型约束与数据审计：`model_v1/reports/EXPERIMENT_CONTRACT.json`、`STARTUP_VALIDATION.json`、`BLOCKERS.json`、`TANK_LABEL_BLOCKERS.json`
- 输入缺失原审计：`reports/INVENTORY_CORRECTION.json`、`reports/MISSING_XPART_HISTORY_SEARCH.json`
- 训练日志：`model_v1/logs/<object>_train.log`
- CAD 验收后台日志：`model_v1/logs/generated_gate_watch.log`

/data 当前空闲 18.16 GB，checkpoint 所在系统盘空闲 299.36 GB。维持 /data ≥15GB；不删除已有实验产物。
