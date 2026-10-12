# V2标签修复与训练前预算门禁

**已修复标签转换并完成三轮602条复测；当前因预算协议冲突停止，未生成V2-100/10,000条、未训练。**

|集合|本轮前|当前|
|---|---:|---:|
|圆/矩形非单侧|14/53（extent修复后）|39/53|
|负距离|65/182（extent修复后）|165/182|
|全Fusion360|235/602（单位修复基线）|570/602|
|此前通过对照|20/20|20/20|

全602条：601执行成功（99.83%），599 STEP重载（99.50%），570联合几何通过（94.68%）；原单位修复基线235条通过样本无回退。32条不进入训练候选：29条几何阈值失败、2条重载失败、1条源轮廓属性校验失败。原41234回退已恢复通过。失败记录保持完整；未删除或覆盖任何旧标签。

## 修复范围

1. 圆心由草图局部坐标转换到世界坐标；Box以矩形中心定位；非轴对齐矩形/四边形使用真实polygon。
2. 轮廓按端点连接并必要时反向，禁止盲目连接断点；圆弧遵循法向右手角度；NURBS使用次数、节点与有理权重求值，不再插值控制点折线。
3. 对复合闭环使用平面图分解和嵌套奇偶规则，生成现有DSL的ExtrudePolygon/Cut/Union。使用源JSON面积与质心独立验证（额外严格校验，非几何Gate放宽）。三个中间版本回归样本均已修复。
4. 有符号/双侧extent逻辑沿用用户已修版本；量纲转换继续缩放height_two，不缩放方向与symmetric。

权威代码：scripts/geometry_pack_v2_mesh2cad/placement_v3/。placement_v1/v2和三轮原始输出均保留；没有改共享转换器。V1入口→出口19,580文件哈希无变化。相对更早冻结基线的cad_dsl.py变化在任务开始时已经存在，记录为用户此前extent修复，不把它误报为本轮修改或回滚。

## Hook证据与真正的阻塞

在20个DeepCAD样本、两个表示臂上调用真实Sonata与_splice_geometry，并在Llama forward入口停止。M2实际有效槽位范围[2, 128]；B1完整edge post-encoder不足M2的样本为6/20；未经修复自然全预算相同为1/20。

|样本|surface|M2辅助有效|B1完整edge辅助有效|M2入口总长|B1入口总长|
|---|---:|---:|---:|---:|---:|
|deepcad__0086_00860845|15|32|15|53|36|
|deepcad__0032_00326198|106|64|46|176|158|
|deepcad__0009_00097993|15|68|15|89|36|
|deepcad__0011_00111806|125|128|44|259|175|
|deepcad__0062_00620744|386|128|118|520|510|
|deepcad__0099_00990920|171|128|118|305|295|

入口总长来自固定的合成probe prompt，不冒充真实训练DSL序列长度。每个样本保留4个几何边界marker和2个普通token，完整六项计数及active mask见budget_probe_v1/RESULTS.json。M2 NaN padding被剥除，插入的辅助槽位mask全部为1。

例如M2=128、B1=44：若补84个mask=0的padding，槽位可相同但有效数量与active attention不同；若改成mask=1，则会把padding算作有效输入；重复token也违反已冻结约束。因此不能在不修改M2协议的前提下，宣称所有六项严格匹配。

建议待用户批准后，为公平预算对照引入共享有效数量K_valid=min(M2可用数, B1 post-encoder数)，两臂确定性选择K_valid；需要固定槽位时再同时使用相同的masked padding。完整曲线仍永久保留，选择索引单独记录。该方案会改变M2的有效输入预算，所以本轮没有擅自实施。另一种选择是只匹配槽位并明确允许active数量不同，但这不符合当前严格门禁。

按照“预算不一致即停，只写报告”的边界，20条probe发现反例后已停止：没有执行2796条修复后dry-run，没有生成新split，也没有进入100条或模型训练。旧Phase0报告仍原样保留；当前报告不伪称Phase0通过。

## 10,000条计划边界

目标按最新指令改为10,000个去重后且标签合格的独立CAD。仅做了目录级候选盘点：DeepCAD raw_json=2,500，Fusion360程序JSON=8,625；后者额外中间STEP/OBJ不能算新CAD。两者合计不等于合格独立数，新增数据源需求待去重/标签筛选后确定。100条工程验证、practical pilot、10,000条扩充都未启动。

另外，已有mesh_edge_to_curve_v1只实现oracle grouping，GT-free版本尚未实现；后续必须从共同practical mesh重新检测30°锐边并图遍历拟合，不能拿oracle结果充当practical输入。官方Llama-3.2-1B-Instruct本地目录存在，训练仍需验证初始化权重来源，不能沿用旧错误checkpoint。

## 技术参考

- [Autodesk Arc3D：角度由法向右手规则定义](https://help.autodesk.com/cloudhelp/ENU/Fusion-360-API/files/Arc3D.htm)
- [SciPy BSpline：节点、系数和次数](https://docs.scipy.org/doc/scipy/reference/generated/scipy.interpolate.BSpline.html)
- [Shapely polygonize_full：多边形与cut/dangle边分离](https://shapely.readthedocs.io/en/maint-2.0/reference/shapely.polygonize_full.html)

这些资料用于实现语义校验，不作为本地通过率的来源。所有数字来自本任务逐样本JSON。
