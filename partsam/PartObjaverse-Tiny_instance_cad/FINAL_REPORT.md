# 批量 CAD 转换结果

输入文件夹：200
STL 总数：2112
成功：2112；失败：0
类型：{'faceted_surface': 2098, 'faceted_solid': 7, 'independent_faces': 7}
原始文件 SHA-256 保持一致：True
完整性异常：0
代码和 CAD 文件共约 20.450 GB

输出目录：`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_cad`

每个源文件对应独立建模代码（内嵌网格数据）、STEP、BREP、验证报告。
开放输入保留为 CAD 曲面；闭合输入转为实体。几何由三角平面构成，未推断原始设计特征。
所有成功 STEP 已重新导入检查；源文件未覆盖。STL 单位未知，保留原始数值和坐标。
零面积退化三角面跳过 7294 个，涉及 142 个文件，详见每件报告。
另外跳过内核精度以下的狭长三角面 48 个，涉及 5 个文件；最小高阈值 1e-7（原始数值单位），所有索引记录在每件报告中。
