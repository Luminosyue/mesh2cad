# V2 数据制作前审计：暂不放行100条训练

## 结论

已逐条审计全部2796条（DeepCAD 2194、Fusion360 602）。本次仅完成标签重放、存储协议核验和保守去重分组；没有制作100条practical数据，没有启动训练，没有改写旧split或V1。

602条Fusion360均存在约10倍单位链路不一致，当前不能直接作为新V2输入。标签几何统计使用原始STEP读入坐标，不通过ICP、缩放搜索或阈值调节隐藏不一致。此处的FAIL不能简单解释为所有Fusion360的拓扑或程序内容错误：单位错误与真实形状误差必须在修复单位合同后分开复测。

## 标签重放结果（初始阈值，尚未冻结）

| 来源 | 数量 | DSL执行 | STEP重载 | 暂定几何Gate通过 | Chamfer_rel中位数 |
|---|---:|---:|---:|---:|---:|
| deepcad | 2194 | 2190 | 2190 | 2190 | 0.003555944674443331 |
| fusion360 | 602 | 601 | 595 | 0 | 0.22231427748154686 |

全体可执行 2791/2796，可重载 2785/2796；暂定几何通过 2190/2796。每条结果、失败阶段、DSL源坐标副本、reconstructed.step均保留。没有使用原始source JSON回退重建来冒充DSL执行成功。

## 指标和范围

重放目标为cad_target.dsl；先按记录的仿射变换逆变换，再用同一CadQuery/OCP DSL执行器导出STEP并重新读入。参考是每条metadata明确指向的model.step。两个STEP都用同一tessellation实现。

Chamfer_rel = 两个方向最近邻欧氏距离均值的平均 / GT tessellation bbox对角线；不平方。每边独立、确定性均匀面积采样20000点，不做对齐。coverage_02 = GT采样点到重放采样点距离/D <=0.02的比例。暂定通过条件是Chamfer_rel<=0.01且coverage_02>=0.98，同时表面文件8192x6且manifest与pack标签AST一致。

这不是模型test性能；读取了全体GT标签和源几何以执行用户要求的数据审计，没有读取test decode输出、预测或模型test指标。样本级几何误差与样本身份分组均可复核。

## Fusion360单位链路

全体602条的surface原始采样bbox对角线约为coordinate_transform.source_diagonal的10倍。所有2796条curve normalization与surface记录的scale/translation字段相同，但相同字段不代表字段对应的输入单位正确。

例：fusion360__102525_06a3094b_0000，官方model.obj的x范围约[-0.195,0.195]，STEP tessellation后的x范围[-1.95,1.95]；V1将从官方OBJ生成的scale=9.3000904用于STEP采样，生成canonical surface x范围约[-16.322,19.949]。对应DSL却是宽3.627035的canonical Box。原STEP显式声明CENTI/METRE；源码build_fusion360_sample.py复制官方STEP和OBJ，而geometry_pack_v1/pack.py重新tessellate STEP后直接套用旧OBJ变换。

应在V2中明确存储STEP文件单位、reader输出单位、DSL源数值单位、统一工作单位，再应用一个共享变换。禁止仅凭metric最优自动选择10或0.1，也禁止永久改动V1。单位合同确认后重新报告无额外对齐的几何指标。

归一化检查另发现14条DeepCAD的detected-edge法向存在非单位值；必须检查零向量/相邻法向抵消并显式保存有效性，不能对零向量盲目归一化。数值误差、数组形状和各样本证据见NORMALIZATION_ROWS.json。

## 去重分组不等于已经得到2796个独立CAD

用source STEP身份、source JSON hash、规范化DSL AST hash以及归一化三角网格fingerprint连接分组，得到2644个候选组，其中79组含多个记录。旧跨split组数按方法分别为{'source_json_hash': 11, 'dsl_ast_sha256': 29, 'geometry_fingerprint': 32}，这些方法相互重叠，不能求和当成重复CAD数。

几何fingerprint保留方向，消除平移和统一缩放，对顶点/三角形重排及朝向翻转不敏感；量化1e-5 bbox diagonal。它仍依赖tessellation，未穷尽重网格或近似形状重复。其中1条Fusion360重放审计150秒超时，未保存几何fingerprint；实际fingerprint覆盖2795/2796。因此候选组数不是“已认证独立CAD数”，FULL_SUMMARY.grouping_complete只表示全部记录已尝试处理。未新划split、未删除任何样本。若新目标必须保持2796个独立CAD，需从合格whole-part候选源补足去重/标签排除造成的缺口，不能把clean/practical计为新CAD。

## 100条配额与训练状态

当前标签Gate通过行的来源/难度计数为{('deepcad', 'simple'): 1625, ('deepcad', 'medium'): 304, ('deepcad', 'hard'): 261}。难度按全部DSL构造器调用计数，包括sketch/boolean；这一定义必须在最终100条选择前固定。曲线>128配额必须从practical meshfit完整曲线计数核验，不能拿oracle计数代替。尚未选择100条，也未退而求其次减少Fusion360配额。

官方Llama-3.2-1B-Instruct本地目录存在，但文件名为config (2).json、model (2).safetensors和tokenizer (2).json等，不是标准from_pretrained布局。未重命名它们，未加载或混用SpatialLM微调语言模型。训练前还需独立整理可追溯模型载入布局，并明确Sonata/C2/projector的初始化来源。

## 实验设计与下一步

按顺序：确认并修复新V2的单位合同 → 复测标签并冻结阈值 → 完成近重复核验、组级划分和必要补样 → 按30/40/30及Fusion360>=30、practical曲线>128至少10条选择100条 → 制作同一mesh/同一次锐边检测驱动的B0/B1/M2输入 → B0/M2 overfit与跨CAD correct/shuffle → 通过后才制作2796版与更大数据。

完整曲线必须保留；128只作为训练时可审计的选择预算。官方SpatialLM轴向约定为axis-aligned、z-up；不独立旋转输入，所有位置、轴和方向参数保持一致。来源：https://github.com/manycore-research/SpatialLM 。新任务的主实验是mesh-derived；oracle单独命名为上界，不与practical B1混比。

需要用户确认：允许先修复V2单位合同，并在去重后补充合格CAD以达到“2796个独立CAD”，还是先接受数量较少的严格合格pilot？本次未自动改变样本总数或标签。

## 复现、保护和限制

V1冻结哈希复核：19580个文件，变化列表=[]。冻结范围覆盖目标DSL、transform、source JSON、表面、检测/锐边点、source STEP、执行器及原surface index cache；不是整个10TB工作区快照。旧训练进程在本轮开始时已不在，未由本次终止或修改。

执行代码：code/audit_v2_labels.py；归一化检查：code/inspect_v2_protocol.py；5个审计单元测试通过。详细报告JSON均在本目录。审计首版_audit_stage1_v1因相对STEP路径处理缺陷中止并保留，其结果不可使用；本版所有2796条路径已规范为绝对路径并通过存在性检查。本版CPU调度从8并发调整至24并发时只更换本次调度器，完成样本未重写；全体结果仍来自相同代码、参数和执行器。

几何数值受tessellation和Monte Carlo点采样影响；曲线局部归一化会丢失全局centroid是另一个表示层问题，未在此自动修改C2。固定practical、噪声在线增强、post-encoder预算和LLM拼接hook尚未实现，不能宣称通过。
