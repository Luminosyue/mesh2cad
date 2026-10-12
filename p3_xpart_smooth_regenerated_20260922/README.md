# X-Part 重新拟合 CAD：交付与验收说明

输入：`/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases`

完整输出：`/data/home/cuiyuehan/project/mesh2cad/p3_xpart_smooth_regenerated_20260922`

本轮对 77 个非 tank case 的 793 个 OBJ 零件重新拟合，tank 跳过。原网格只读，逐件记录并复核 SHA-256；未将旧 CAD 复制为本轮结果，也未使用三角片缝合 B-Rep 作为兜底。

## 实际状态

{"ACCEPTED": 576, "NEEDS_REFINEMENT": 217}

完整成果包数量：793。独立重建审核：793 / 793。

`ACCEPTED` 表示有效 CAD 且通过本次采样误差阈值；不是制造公差认证，也不表示所有零件都经过逐件外观验收。`NEEDS_REFINEMENT` 是有可查看的 CAD 但误差超限或已发现外观缺陷。`FAILED` / `TIMEOUT` / `INCOMPLETE` 不算交付成功。

## 生成方法

从各零件原始 OBJ 重新采样、剖切，按形状选择球面、轮廓拉伸、样条剖面旋转、周期 B 样条截面曲面或含分支及孔洞的多曲面组合。只在拟合输入过密时进行简化，最终距离仍针对完整源网格。

旋转剖面按多段构造。部分周期 NURBS 面沿参数方向分为六条面片，保留同一几何曲面，便于显示真实 B-Rep 面片边界。因此图中的部分线是建模分面边界，不代表原物体存在棱线；没有将轮廓线伪装成 B-Rep 边界。

所有成功输出均经过 STEP 回读。显示用三角网格和曲线来自该 STEP；OpenCASCADE 提取边、识别周期接缝，主图隐藏接缝。每条曲线保存 256 个点，优先等弧长采样，失败时在 JSON 中明确记录均匀参数采样。边界数量随零件变化，不固定为轮胎的 9 条。

VTK 使用正交相机、平滑法线和抗锯齿；Pillow 排版。边界图 2000×1630，源网格与 CAD 对比图 2000×860，左右采用同一坐标变换与比例。

## 验证与限制

对 STEP 回读后的网格与完整源网格分别采样 10,000 点，计算双向点到三角面的距离。距离按源包围盒对角线归一化：平均值 ≤ 0.3%，P95 ≤ 1%，采样最大值 ≤ 4%。当原网格有有效体积时，体积误差另要求 ≤ 10%。采样最大值不是精确 Hausdorff 上界，不能保证捕捉所有细小孔洞、尖角或波纹。

对非封闭源网格，体积项不适用；CAD 封口、孔洞和分支连接包含拟合推断。复杂曲面可能有波纹、细节损失或局部拓扑差异；请通过预览与报告确认使用范围。未达到条件的零件已单独列出，不计入通过数。

几何保留原始数值坐标、位置和比例。输入未提供物理单位，STEP 的单位声明不构成对真实毫米尺寸的确认。装配或加工前需要核对单位。

独立审核将 `cad.py` 单独复制到临时目录执行，不读取源网格；比较新 STEP 的有效性、面/边/实体数、包围盒、面积、体积及曲面距离，并核对边界采样与图片尺寸。若独立三角化造成采样差异，用有效曲面点的 B-Rep 距离进一步校验。详情在服务器 `validation/`。

## 文件与复现

每个零件位于 `cases/<case>/PART_###/`，包含 `cad.py`、`parameters.json`、`model.step`、`model.brep`、`model.stl`、`curves.json`、`curve_samples_256.npz`、`render_transform.json`、两张 PNG 及 `report.json`。失败条目可能没有全部文件。

在安装 CadQuery 2.6.1、NumPy 的 Python 环境中，把单个 `cad.py` 复制到新目录，然后运行 `python cad.py`，即可生成该目录中的 STEP/BREP/STL。脚本内嵌拟合参数和构造代码，不依赖原 OBJ。

批处理与渲染代码位于 `scripts/`。环境还使用 trimesh 4.11.5、SciPy、Shapely、Open3D、VTK 9.3.1、Pillow；Linux 无显示器渲染通过 `xvfb-run -a` 启动，中文字体为 `scripts/msyh.ttc`。完整重新拟合命令：`xvfb-run -a python3 scripts/regenerate_smooth.py --workers 16 --force`。该命令会更新本输出目录，请先备份需要保留的结果。

离线打开 `index.html` 查看全部零件的压缩预览；原尺寸 PNG 和 CAD 文件保存在上述服务器路径。`manifest.csv`、`manifest.json` 和 `summary.json` 提供逐件指标及汇总。
