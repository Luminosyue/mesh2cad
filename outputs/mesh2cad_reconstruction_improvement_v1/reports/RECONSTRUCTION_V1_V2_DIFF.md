# RECONSTRUCTION_V1_V2_DIFF

V1：世界/PCA轴打分，最多两轴 silhouette extrusion，加一个bbox和一个平均范围圆柱；按strict、IoU、NCD挑选。没有局部截面、平面组件或参数搜索。

V2：保留并重新执行V1最优候选作为incumbent；由source family约束开放平面区域候选；按法向与点到平面残差聚类，合并三角形为二维轮廓；最多7个区域、96个轮廓顶点、6次Boolean，禁止单三角区域和三角轮廓，拒绝高复杂度面片封装。加入历史截面tracking的紧凑6截面×12点loft，仅允许单outer track，不静默丢失hole。新增表面法向轴枚举、最小二乘球体候选。

对开放平面区域采用0.0002、0.001、0.004 canonical厚度的有限搜索。厚度没有被源表面观测到，始终记录thickness_assumed。这提供几何一致的薄实体候选，不恢复原始壁厚或设计历史。没有为单case设置尺寸，没有改变输入或补全mesh。

每例最多8个候选；执行后的STEP必须重载后再tessellate。排序：先满足原strict gate，再最小化10*NCD+(1-IoU)+2*surface_centroid_error+bbox_error。初始score、最佳score、候选数、搜索步数和最佳ID均保留；达到strict即通用早停。离散轴/厚度搜索已经实现；通用连续优化、revolve/cone、复杂语义Boolean和LLM planner未实现，不能声称已完成所有推荐family。

历史复用组件为candidate_axes、basis_for_axis、projected_profile、section_loft_profile及其loop tracking依赖；仅复制纯函数，新emitters直接生成原生CQ。旧DSL、导出/删除逻辑与静默Boolean失败逻辑未复用。V1 evaluator和occupancy源码逐字节相同；源文件和canonical mesh/transform同样逐字节匹配。

提高覆盖率不是通过降低阈值。严格接受的薄实体仍是pseudo-CAD supervision；不等于物理实体、原始体积或原始设计GT。自由形状/复杂分离表面超出预算时保留失败，不增加几十个primitive来拟合三角网格。
