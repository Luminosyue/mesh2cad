import pathlib,json,hashlib
from fusion_units_probe import R,save
O=R/'cad_spatial_dataset/geometry_pack_v2_mesh2cad/unit_audit_v2'
def main():
 gate=json.loads((O/'UNIT_LABEL_GATE.json').read_text());qa=json.loads((O/'IMPLEMENTATION_VALIDATION.json').read_text())
 assert qa['passed'] and gate['v1_hash_check']['passed']
 rows=json.loads((O/'results602.json').read_text());failed=[r for r in rows if r.get('label_gate') is not True]
 save(O/'NONPASSING602_SUBSET.json',failed)
 extra='''

## 最终验证补充

- 单位合同602/602；逐样本验证surface坐标变换、法向逐位不变、行序、共用尺度、操作顺序与方向向量：602/602通过；4项单元测试通过。此结果不等同于标签几何Gate、post-encoder预算Gate或practical曲线Gate通过。
- 执行601/602=99.83%；重载593/602=98.50%，低于99%；联合几何235/602=39.04%。因此门禁明确阻断，无需先设一个更宽的“可接受几何通过率”。
- 剩余：358个几何阈值失败、8个重载失败、1个执行失败；详见NONPASSING602_SUBSET.json。
- 原超时fusion360__23658_c75a430c_0000：上限600秒，3.446秒后报Standard_OutOfRange('NCollection_Sequence::ChangeValue')，为执行异常而非几何比较失败。独立日志位于logs/同名.log，结构化错误在samples/同名/audit.json。没有继续重试或把它算成timeout。
- 旧bbox精确统计594条可用，旧几何距离指标595条可用；有1条旧形状可tessellate但精确CAD属性读取失败，另有6个旧重载失败和1个旧超时。两种分母不得混用。旧损坏/缺失STEP读取可能造成OCP原生进程崩溃，最终报告脚本使用子进程隔离，记录在baseline_ratios_isolated.json。
- 源timeline没有额外LOFT/SWEEP等被跳过的Feature，但profile中存在NurbsCurve3D；不能排除轮廓离散近似问题，更不能声称已证明全部残差原因。53条圆/矩形非单侧拉伸风险均未通过；182条带负extent距离，其中162条未通过；这些集合重叠，不应相加。
- 权威汇总脚本为fusion_units_report_v2.py（旧fusion_units_report.py尝试在主进程读取坏STEP而中断，未生成报告，保留原文件）。所有审计和代码仅写V2新目录；两个首轮尝试保留可追溯记录。
- 下一步应单独授权修复DSL转换器的拉伸方向、双侧/对称范围、轮廓位置与曲线近似，再按原阈值复测。当前不修这些语义、不制作100条、不训练、不重新切split。
'''
 with (O/'FUSION360_UNIT_FINAL_REPORT.md').open('x') as f:f.write((O/'FUSION360_UNIT_REPORT.md').read_text()+extra)
 files=list(O.rglob('*'))+list((R/'scripts/geometry_pack_v2_mesh2cad').glob('*.py'))
 manifest={}
 for p in files:
  if p.is_file():manifest[str(p)]=hashlib.sha256(p.read_bytes()).hexdigest()
 save(O/'DELIVERY_SHA256.json',manifest)
 print('FINAL_VALIDATED',len(manifest),'files')
if __name__=='__main__':main()
