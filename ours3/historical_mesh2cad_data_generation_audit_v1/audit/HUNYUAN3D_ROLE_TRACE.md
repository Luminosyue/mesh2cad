# P3 / Hunyuan 角色溯源
所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。

HUNYUAN3D_USED=YES（Hunyuan3D-Part/X-Part 产物支线）；P3_USED=YES。
HUNYUAN3D_ROLE=MESH_ONLY_SOURCE（已验证主支线；准确描述是 mesh-conditioned part completion）。IMAGE_TO_MESH 为另一个已实现但运行产物未闭合的支线。枚举没有 MESH_TO_COMPLETED_PART，故不能误填 CAD_TO_RENDER_TO_MESH。

## 已验证：mesh → P3-SAM → X-Part
`/data/home/cuiyuehan/project/mesh2cad/scripts/xpart_from_p3.py:57-169` 读取 `part_metadata.json`、原零件 obj 与坐标变换，采样 surface points / bounding boxes，调用 PartFormerPipeline；输出 `generated_mesh_norm.obj`、`generated_mesh.obj`、`complete_part_NNN.obj` 和 assembly GLB。`/data/home/cuiyuehan/project/mesh2cad/scripts/run_p3_xpart_dora_frontend_v1.py:301-436` 也明确以 source mesh 进行 P3 bbox/face segmentation，再 X-Part 完成几何。这里渲染主要用于 QA，不是 Hunyuan 输入。
后端 `/data/home/cuiyuehan/project/mesh2cad/p3_xpart_open_cases/_cadquery_batch_code_20260922/feature_runtime.py` 根据截面/轮廓参数建 extrude/revolve/loft CadQuery；或者 CADFit greedy search 重建。CAD 来自后续拟合，不是 Hunyuan 配套设计 GT。训练用 20-case frozen manifest 中 MESH_PATH=complete_part OBJ，CAD_PATH=xpart_parts_cadquery_features Python，STEP_PATH=同一 fitted target，明确 mesh-first。
Toaster 初始报告：39 source parts / 39 X-Part success，3 P1 smoke pass，full39_ran=false。存在后续更多 DSL/STEP 文件，因此初始报告不是整个目录的最终产物计数。

## 已实现：image → Hunyuan3D-2mini → mesh → CADFit
`/data/home/cuiyuehan/project/mesh2cad/CADFit/image_to_cad/shape_gen.py:27-34,55-100`：单图片，不是 text；可去背景；model=tencent/Hunyuan3D-2mini，subfolder=hunyuan3d-dit-v2-mini-turbo，steps=5、octree_resolution=380、chunks=20000、guidance=5、seed=12345（均为源码默认，不是已证实历史运行配置）。输出 trimesh mesh，调用者保存 raw.glb。
`/data/home/cuiyuehan/project/mesh2cad/CADFit/image_to_cad/run_image_to_cad.py:99-127`：raw.glb → Taubin/decimate STL → process_single_stl → best greedy Python/STL。项目全文件 inventory 未发现名为 raw.glb 的产物；自定义输出路径或项目外运行无法排除。历史成功 N=UNKNOWN。对应 CAD 为后续 CADFit 重建，原始 CAD GT=UNKNOWN。

## CAD → render → Hunyuan 审计
CAD_TO_RENDER_TO_HUNYUAN_VERIFIED=UNKNOWN / NOT_FOUND_IN_AUDITED_EVIDENCE。
未恢复连接 CAD source、render camera、image hash、Hunyuan invocation 与 mesh/CAD pairing 的 manifest。camera count/resolution/config=UNKNOWN；不能用 GPT pilot 的 8幅320x320源 mesh视图填充这个空缺，也不能把 Hunyuan 仓库 demo 能力当历史执行。

## 下载的 HY3D NPZ
mesh2cad/ 与 mesh2cad_stl_* 包含 `full.ply`、`part_N.ply` 的 NPZ/转换 STL。上游每个网格是否由 Hunyuan 生成 UNKNOWN。固定 NPZ100：11可读/89截断，64可读parts中15严格有效，pilot20=0。后续转换摘要：940 NPZ、89可读、851截断、626 parts。它们是不同快照/统计母集。不能把 NPZ100 的 11 推广到全库，也不能凭 HY3D 名称判断 CAD-first。
