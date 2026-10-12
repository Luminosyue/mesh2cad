# Mesh 后处理与 tessellation
所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。

| 支线 | 已恢复行为 | 证据与限制 |
|---|---|---|
| PartObjaverse Stage A / PartSAM extract | 按 instance labels 取原 faces，scene coordinates，保留 source hashes | pipeline.py audit_extract_one；不是新生成CAD源mesh |
| PartSAM P1 | process=True、nondegenerate_faces、remove_unreferenced_vertices；bbox diagonal归一至6，DSL/surface/curve共用变换 | build_partsam_p1.py:97-135 |
| LLM pilot | 源mesh保持，CAD工作比例x1000，重建mesh x0.001对比 | evaluate_round.py + geometry report |
| PartObjaverse Stage B | CAD工作最大extent100；指标再折算最大extent1 | stage_b_pipeline.py:123-130 |
| P3/X-Part | mesh normalize及逆变换、part completion，不能称简单watertight repair | xpart_from_p3.py:80-140 |
| Image Hunyuan实现 | duplicate/null face cleanup、小组件阈值200、可选hole fill200、Taubin20(0.5,-0.53)、50K quadric decimation | mesh_preprocess.py；trimesh fallback另含fix_normals，运行证据UNKNOWN |
| CADFit | normalize、轮廓/候选搜索；raw尺度与aligned指标分离 | CADFit geometry_provenance_report.md |
| Synthetic CAD-first | CadQuery shape多tolerance导出STL，目标三角预算选择 | export_high_mesh.py |
| HY3D NPZ audit | 解码PLY bytes，未repair/remesh/weld | hy3d watertight audit |

noise augmentation/remesh/subdivide 在搜索候选中出现，不代表以上主要历史pair统一经过这些步骤。逐数据集未闭合的历史启用状态写 UNKNOWN。

LIKELY_DIRECT_CAD_TESSELLATION=YES（CADFit synthetic demo 的 input_high_mesh 与各重建 STL 的源码+历史产物证据）；不是对所有 source mesh 的全局结论。
`/data/home/cuiyuehan/project/mesh2cad/CADFit/scripts/synthetic_high_mesh_two_case/create_ground_truth_cases.py` 定义 GT Python 和 STEP；`/data/home/cuiyuehan/project/mesh2cad/CADFit/scripts/synthetic_high_mesh_two_case/export_high_mesh.py` 从同一个 build_model 导出高密度 STL。STEP 与 mesh 共同来自 CAD body，但并非所有实现都按“先落STEP再读STEP再tessellate”的顺序。
本轮 RETESSELLATION_RUN=NO，GEOMETRY_EQUIVALENCE_NEW_TEST=UNKNOWN。严格遵守禁止生成mesh/STEP；已有源mesh与重建mesh明显不同的实例由历史IoU/CD和源路径佐证。没有新顶点/三角一一匹配结果，不能伪装成已测。
