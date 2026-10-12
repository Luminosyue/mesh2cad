所有路径相对项目根目录 /data/home/cuiyuehan/project/mesh2cad/。结论级别：源码+产物交叉验证 / 历史报告 / UNKNOWN。仅静态审计；本轮没有重新执行 CAD、STEP、mesh 或训练。


选择规则：对最终 top1000.csv 的 468 行按 case_id 字典序取前 3，不按 IoU、图片或人工观感选择。这里只追溯这 3 个 case 的链条，不能外推所有目录。


当前路径复核：3个case的source.obj均存在且与历史SHA一致；其历史上游GLB和instance label引用共6条目前均不存在，无法重核上游SHA。下面记录的object/label哈希是历史provenance证据，不是本轮验证结果。见 integrity/REFERENCE_VALIDATION.json。保留原始OBJ仍可复用后半段拟合流程，但完整GLB→labels→OBJ重现条件不满足。

## 002e462c8bfa4267a9c9f038c7966f3b_part_000

源 mesh=`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_000/source.obj`；上游 object=`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_mesh/002e462c8bfa4267a9c9f038c7966f3b.glb`；face labels=`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_gt/002e462c8bfa4267a9c9f038c7966f3b.npy`。

原始 GLB sha=ff373033f00fa8ce88fd9a0a3e57c75c621bb87bf140c1e294ffd30b2ad7b81f；label sha=f9f874fe6df391e5888e6d71c3ab432e928239776eb6b3f6477a4e938bd49053；OBJ provenance sha=b5e3eaeeee7efa3dbf5134d35fba783870558af52ff2c180c120bc26e78f8321。本轮 OBJ SHA 一致=True。

生成顺序：GLB + instance labels → 按 face id 提取 source.obj → projected_profile / section_loft_profile / primitive_profile 候选 → cad_code(spec) → cad.py → execute_cad → reconstructed.step + reconstructed.stl → IoU/CD → 去重/复现 → top1000.csv。

输入脸数=5088；组件数=261；source watertight=0；坐标策略=original_glb_scene_coordinates_no_normalization。

CAD language=CADQUERY；LLM/API=NO；prompt=NOT_APPLICABLE；CAD exec=True，STEP reload=True，IoU128=0.985754103，NCD=0.004271110。

source.obj 是真实源对象零件，不是此 CAD 的 tessellation；reconstructed.stl 才是 CadQuery 导出网格。源与目标属于同一零件，但 CAD 是 pseudo target，不是原设计 GT。

证据 `/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_000/source_provenance.json`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_000/parameters.json`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_000/cad.py`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_000/cad_execution.log`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_000/metrics.json`；生成器 `/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/scripts/pipeline.py:169-254,555-660,835-916`。

| artifact | bytes | SHA256 |
|---|---:|---|

| cad.py | 4974 | 4ebdac7f409b03932d0c67b65b742aa9d0d4dc3cbcdd775490ff28852c53dd1b |

| cad_execution.log | 16 | 169f24774e13a79b6341d6c41c58f159e180701e87e9028aa70afdf8712b6fbb |

| metrics.json | 5758 | ec7b510565914de229d5592a4395810097a73399b5a04b97d3ecd2d73dc44cbb |

| parameters.json | 5724 | bc7a47a0c2b3d04e382cccf3871f8ae35c777af88acb6a219f8c2ea48083ff5c |

| reconstructed.step | 286773 | 323974906c8e66e76d30cb07f366e7fb65598741b2317fcd9103d089a4995640 |

| reconstructed.stl | 14684 | dcbbefcd896d6ce14a195496262e6290c494926c58948fb7eeec63269eea9e0d |

| source.obj | 409116 | b5e3eaeeee7efa3dbf5134d35fba783870558af52ff2c180c120bc26e78f8321 |

| source_provenance.json | 1533 | 44a0d379c5de45bd80b52d653bc324971e720fc61cd31418390bf72b1b61b247 |

| status.json | 247 | d2962e08ddf2c8fb2377879a87e9ff96c452b4ac8edfee5c6530e476e7098ead |

| transform.json | 745 | 1d7ab3ccf074095a2ce9d86aef2786b9e6a272699bbb0e52da862ae96c55dc4d |

## 002e462c8bfa4267a9c9f038c7966f3b_part_001

源 mesh=`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_001/source.obj`；上游 object=`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_mesh/002e462c8bfa4267a9c9f038c7966f3b.glb`；face labels=`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_gt/002e462c8bfa4267a9c9f038c7966f3b.npy`。

原始 GLB sha=ff373033f00fa8ce88fd9a0a3e57c75c621bb87bf140c1e294ffd30b2ad7b81f；label sha=f9f874fe6df391e5888e6d71c3ab432e928239776eb6b3f6477a4e938bd49053；OBJ provenance sha=eac11a895cb185a63bf218a823574b817dc80d80ec9aa884786318373cc08897。本轮 OBJ SHA 一致=True。

生成顺序：GLB + instance labels → 按 face id 提取 source.obj → projected_profile / section_loft_profile / primitive_profile 候选 → cad_code(spec) → cad.py → execute_cad → reconstructed.step + reconstructed.stl → IoU/CD → 去重/复现 → top1000.csv。

输入脸数=2880；组件数=974；source watertight=0；坐标策略=original_glb_scene_coordinates_no_normalization。

CAD language=CADQUERY；LLM/API=NO；prompt=NOT_APPLICABLE；CAD exec=True，STEP reload=True，IoU128=0.991824280，NCD=0.004263304。

source.obj 是真实源对象零件，不是此 CAD 的 tessellation；reconstructed.stl 才是 CadQuery 导出网格。源与目标属于同一零件，但 CAD 是 pseudo target，不是原设计 GT。

证据 `/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_001/source_provenance.json`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_001/parameters.json`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_001/cad.py`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_001/cad_execution.log`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_001/metrics.json`；生成器 `/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/scripts/pipeline.py:169-254,555-660,835-916`。

| artifact | bytes | SHA256 |
|---|---:|---|

| cad.py | 179269 | 2deb27ad319a891e93e949d5c7eda62124d1d6b9998a5752b80ce7faa8efc43e |

| cad_execution.log | 16 | 169f24774e13a79b6341d6c41c58f159e180701e87e9028aa70afdf8712b6fbb |

| metrics.json | 5746 | a7bda487b312af8acd88da5eafe57c3251d420c71232eb2764136505461e1f93 |

| parameters.json | 279801 | 128a23c041c5d62aa13126d0680b5168e41176839987703b0784dcbd9443dcb5 |

| reconstructed.step | 8477514 | 50df6a80b7de207df4311f842824dda8573da21ad7f7e60424339faeff47654e |

| reconstructed.stl | 1312284 | da23aa0e1e2d21956e217ceb8b8cd271cd2b10d9f7b0cab99c710f6f78b4b796 |

| source.obj | 380511 | eac11a895cb185a63bf218a823574b817dc80d80ec9aa884786318373cc08897 |

| source_provenance.json | 1548 | 869470f604f3257370c8d0b90658691a6c019c3674166f9d16ed09361d8f6637 |

| status.json | 247 | 8d4af901137792502760ea75482ee3d4686ab9fcd22f4a12318679f6724e6f72 |

| transform.json | 745 | 1d7ab3ccf074095a2ce9d86aef2786b9e6a272699bbb0e52da862ae96c55dc4d |

## 002e462c8bfa4267a9c9f038c7966f3b_part_003

源 mesh=`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_003/source.obj`；上游 object=`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_mesh/002e462c8bfa4267a9c9f038c7966f3b.glb`；face labels=`/data/home/cuiyuehan/project/mesh2cad/partsam/PartObjaverse-Tiny_instance_gt/002e462c8bfa4267a9c9f038c7966f3b.npy`。

原始 GLB sha=ff373033f00fa8ce88fd9a0a3e57c75c621bb87bf140c1e294ffd30b2ad7b81f；label sha=f9f874fe6df391e5888e6d71c3ab432e928239776eb6b3f6477a4e938bd49053；OBJ provenance sha=0544225744f9efdbc5240c95ae1e4f49db81619132ce21d9be1c365733c6b6f5。本轮 OBJ SHA 一致=True。

生成顺序：GLB + instance labels → 按 face id 提取 source.obj → projected_profile / section_loft_profile / primitive_profile 候选 → cad_code(spec) → cad.py → execute_cad → reconstructed.step + reconstructed.stl → IoU/CD → 去重/复现 → top1000.csv。

输入脸数=3648；组件数=838；source watertight=0；坐标策略=original_glb_scene_coordinates_no_normalization。

CAD language=CADQUERY；LLM/API=NO；prompt=NOT_APPLICABLE；CAD exec=True，STEP reload=True，IoU128=0.993761116，NCD=0.005258126。

source.obj 是真实源对象零件，不是此 CAD 的 tessellation；reconstructed.stl 才是 CadQuery 导出网格。源与目标属于同一零件，但 CAD 是 pseudo target，不是原设计 GT。

证据 `/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_003/source_provenance.json`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_003/parameters.json`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_003/cad.py`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_003/cad_execution.log`、`/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/candidates/002e462c8bfa4267a9c9f038c7966f3b_part_003/metrics.json`；生成器 `/data/home/cuiyuehan/project/mesh2cad/partsam_cad_iou_top1000_v1/scripts/pipeline.py:169-254,555-660,835-916`。

| artifact | bytes | SHA256 |
|---|---:|---|

| cad.py | 176284 | f4becf10554464b912b128dd98543b9e7af4f8f464c3034f927a54d63669fe25 |

| cad_execution.log | 16 | 169f24774e13a79b6341d6c41c58f159e180701e87e9028aa70afdf8712b6fbb |

| metrics.json | 5806 | 30dd34751d698100ca381c69ecf906c541a8227a831604f9beb2a55731814d85 |

| parameters.json | 276816 | 91a4c39d20d421f4ed194806fa425bc2d46fabce3c03e5dc2282a715ff2c777d |

| reconstructed.step | 1147090 | 09b2015c29834bd2fd235b258dba72c790d12e1d5b906b41b70d4489b1116bbe |

| reconstructed.stl | 19729784 | c9248ef0a62874d53aef045343c2c131fba432388e0a6f37a88fbe52ec60caef |

| source.obj | 417781 | 0544225744f9efdbc5240c95ae1e4f49db81619132ce21d9be1c365733c6b6f5 |

| source_provenance.json | 1550 | c4bc5755ff69c071c47dc70bcb100582da488d7c7496b3a91bfa97d4d61529a2 |

| status.json | 245 | 0cca1d8a5ff5e4eb6a179be4abfefd25cb1514567c237eff93a6825b4b024b23 |

| transform.json | 745 | 1d7ab3ccf074095a2ce9d86aef2786b9e6a272699bbb0e52da862ae96c55dc4d |
