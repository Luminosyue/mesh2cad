from regenerate_smooth import *
from smooth_visualize import extract_and_render
od=OUT/'cases/3d_dollhouse_sofa/PART_001'
r=json.loads((od/'report.json').read_text());r.update(status='NEEDS_REFINEMENT',numeric_gates_passed=passed(r['quality']),visual_review='抽查发现边缘波纹，距离误差通过但外观仍待改进。均匀截面重采样及128点轮廓重试未得到兼顾精度与外观的更好结果。')
actual=cq.importers.importStep(str(od/'model.step')).val();cm=trimesh.load(od/'model.stl',force='mesh');source=load(r['source_path'])
r.update(**extract_and_render(actual,cm,od,r,source));dump(od/'report.json',r)
print(r['status'],r['visual_review'])
