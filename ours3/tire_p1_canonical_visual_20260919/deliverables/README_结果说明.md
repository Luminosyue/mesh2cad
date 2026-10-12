# 轮胎 STL → P1 CAD 与曲线拟合

## 结论

正式选定的 P1 checkpoint-8000 在本 STL 上生成至 4096 token 上限，输出被截断，DSL 解析失败，没有可用 CAD。另复跑了已有轮胎实验所用的末步 checkpoint-39980；交付的 tire_p1.step 来自这个末步权重，不能当作正式 checkpoint-8000 的成功结果。

末步 STEP 重新导入验证：有效性 True，1 个实体，34 个面。几何有效不代表轮胎重建准确，请直接查看 mesh_vs_p1_cad.png。

## 本次输入及流程

- 输入：服务器原有 tire_part006_p1_inference_20260919/source.stl，与参考图轮胎外观一致；本地保存为 tire_input.stl。
- SHA256：6c2386a98c8866326526f9c67ce0612f74b8cece4d8acd7aecefe27e36d3921f。
- 网格：6650 顶点、13296 三角面，闭合。STL 不携带可靠的物理单位，本报告保留原坐标数值，不擅自指定毫米。
- 表面采样：8192 点与法向；包围盒对角线归一化至 6。
- 网格二面角阈值 30°，436 条锐边段，保留 24 条链；每条重采样 32 点，使用冻结 C2_frozen_v1 编码为 256 维 token。
- P1 采用双流表面与曲线输入，贪心解码，bfloat16，最多 4096 个新 token。预测 DSL 经既有执行器导出 STEP，并逆变换回输入坐标。
- 正式 P1 冻结记录的训练曲线输入来自 GT BRep。本次只有 STL，使用既有网格锐边适配，属于输入分布不同的实际推理。

## 曲线拟合效果

24 条曲线中，14 条圆/圆弧、9 条直线、1 条椭圆。逐曲线原拟合器 RMS / 输入包围盒对角线的中位数为 0.0109%，最大值为 0.5664%。这是局部曲线误差，不是 CAD 表面误差，也不衡量轮廓覆盖率。

curve_fit_overview.png 显示网格位置上的曲线；curve_fit_gallery.png 展示全部 24 条曲线的局部 PCA 平面投影。蓝线为网格链、蓝点为编码采样点、橙线为拟合曲线。拟合统计来自原拟合器；另在 JSON 中提供采样点到稠密拟合曲线的近似距离。

多数短弧拟合贴近输入，但第 4 条折线被选为直线，第 11 条椭圆存在明显偏差。当前链条零散且未闭合，较小的局部 RMS 不能说明已恢复完整轮胎轮廓。

**模型实际编码的是重采样网格曲线及切向，不是橙色解析拟合曲线。** 解析拟合用来分类与诊断可视化，本次未改动模型输入以改善外观。

## CAD 与输入的比较

统一使用原始坐标，不进行 ICP、旋转或尺度后对齐。每个网格各采样 30000 个表面点，以双向最近邻距离计算：

- 对称平均表面距离 / 输入对角线：15.564%。
- 双向距离合并后的 95 分位数 / 输入对角线：40.444%。
- 输入三轴尺寸：[0.18965336680412292, 0.18566837906837463, 0.11354917287826538]。
- 输出三轴尺寸：[0.10390101373195648, 0.10361599922180176, 0.24871399998664856]。

上述为采样近似、未平方距离；不是精确 Hausdorff 距离。有效 STEP 的具体几何质量以这些误差和同视角图共同判断。

## 文件

- tire_p1.step：末步 checkpoint-39980 的 CAD。
- tire_p1.dsl：原始坐标 CAD 程序；tire_p1_preview.stl：CAD 三角化预览。
- tire_input.stl：本次输入。
- mesh_vs_p1_cad.png：同坐标、同尺度、同视角比较。
- curve_fit_overview.png、curve_fit_gallery.png：曲线可视化。
- interactive_viewer.html：离线交互 3D 查看器，浏览器打开，可旋转、缩放、显示/隐藏曲线与叠加网格。
- geometry_metrics.json、curve_fit_metrics.json、curve_fits.json、step_validation.json：测量和拟合参数。
- inference_record.json：末步推理记录；checkpoint8000_failure_record.json 与 checkpoint8000_failed_generation.txt：正式权重失败记录。
- reproduction_scripts/：本次服务器脚本，固定服务器根路径。

服务器运行目录：/data/home/cuiyuehan/project/mesh2cad/ours3/tire_p1_canonical_visual_20260919
复现顺序：在原 spatiallm 环境执行 setup_tire.py → prepare_tire.py → decode_tire.py --arm B（正式权重）或 --arm D（末步权重）→ fit_diagnostics.py → visualize_p1.py；在 cadfit-env 执行 validate_step.py；在 spatiallm 执行 interactive_p1.py。准备曲线与推理使用 CUDA_VISIBLE_DEVICES=6，均未训练或修改权重。
