# GEOMETRY_BUDGET_AUDIT

来源：真实 `train_v3_smoke.encode()` + `one_forward()`（StopAtLlamaEntry，读取 `inputs_embeds.shape[1]`）。
800/800 forward 成功。未改 Dora / C2 / 正式 V3。

## 公式拆解

```
geometry_extra = B1.total_llm_input_length - k_valid + SUMMARY_TOKENS(8)
```

| 项 | 真实含义 |
|---|---|
| `B1.total_llm_input_length` | V2 gate 用 **dummy 8 token** 钩子 splice 后的长度：`6 kept + S_surface + 128 B1 padded slots`。**不含 CAD DSL，也不是 V3 训练序列。** |
| `k_valid` | `min(B1_post_encoder, M2_c2, 128)`，选中的第二条流条数 |
| `+ 8` | V3 adapter 的 summary token 数 |

V2 probe 实际插入的是 **128 物理 slot**，不是 `k_valid`。因此：

```
geometry_extra = S + 142 - k_valid
real_M2_expansion = (S-1) + (8-1) = S+6
geometry_extra - real_expansion = 136 - k_valid   # 实测 min=8, max=135
```

从 dummy probe 反推 `S = B1.total_llm_input_length - 134`，与真实 Sonata 输出 **800/800 完全一致**（inferred_vs_measured = 0）。

## 六个问题

1. **简单 CAD geometry_extra≈140？**  
   Sonata 表面 token 很少（min S=15，Box `0005_00051866` S=60）。`geometry_extra≈S+142-k`，k≈12 时约 190；更小 S + 较大 k 可到 140。

2. **复杂 CAD 为什么到 3970？**  
   最大值 `fusion360__32219_e5edc7ce_0034`：S=**3832**，k=4，`B1.total=3966`，`geometry_extra=3970`。几乎全是 Sonata 表面 token。

3. **主要贡献是谁？**  
   **Surface / Sonata**。S 与 geometry_extra 相关 **0.9995**。B1 在 V3 里不再以 128 slot 进入 LLM。M2 只有 8 个 summary。

4. **M2 只有 8 个 summary，为何 budget 仍接近 4k？**  
   8 个 summary 几乎可忽略。`<|point_pad|>` 被替换成 **可变长度 Sonata token**（max 3832）。表面流吃掉 context。

5. **B0 / B1 / M2 真实 LLM sequence length**  
   同一 CAD、同一截断 target：B1-V3 与 M2 **完全相同**（都 splice 8 summary）。B0 无第二条流，约短 10 token。

6. **accounting bug？**  
   **是。** `geometry_extra` 比真实 M2 expansion 多 `136-k_valid`（128 的 phantom padding + dummy 钩子残差）。  
   但 `prompt + real_expansion + supervised_target` 与 `inputs_embeds.shape[1]` **一致**（无 splice offset）。  
   这个 bug 让 encode **过度截断** GT：64 条被 `target[:allowance]`，其中 **5 条其实放得下完整 GT**。

## 分布

| metric | min | median | p90 | p95 | p99 | max |
|---|---:|---:|---:|---:|---:|---:|
| geometry_extra | 140 | 296.0 | 2753.5 | 3191.2 | 3804.2 | 3970 |
| surface_encoder_output_tokens | 15 | 206.5 | 2636.2 | 3063.3 | 3670.3 | 3832 |
| real_M2_geometry_expansion | 21 | 212.5 | 2642.2 | 3069.3 | 3676.3 | 3838 |
| extra - real_expansion | 8 | 112.0 | 132.0 | 134.0 | 134.0 | 135 |
| inputs_embeds.shape[1] | 134 | 734.0 | 3707.3 | 3980.0 | 4064.2 | 4088 |

- S>1000: 158 / 800
- S>2000: 132 / 800
- S>3000: 47 / 800
- encode 截断: 64
- 完整 GT+EOS 真实能进 4096: **741**
- encode 截断但真实能放下: **5**
- encode 未截断但真实放不下: **0**

## 五个重点样本（M2）

| cad_id | S | m2_summary | prompt | DSL raw | supervised | geometry_extra | real_expansion | embeds | EOS in labels |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| deepcad__0005_00051866 | 60 | 8 | 36 | 92 | 92 | 190 | 66 | 194 | True |
| fusion360__63539_dd7fddaa_0005 | 3056 | 8 | 36 | 19289 | 990 | 3070 | 3062 | 4088 | False |
| fusion360__30400_8824ce97_0007 | 2326 | 8 | 36 | 10874 | 1720 | 2340 | 2332 | 4088 | False |
| fusion360__109232_04340d62_0014 | 3795 | 8 | 36 | 7179 | 145 | 3915 | 3801 | 3982 | False |
| fusion360__50409_4a322fbf_0009 | 2623 | 8 | 36 | 4797 | 1423 | 2637 | 2629 | 4088 | False |

### B0 / B1 / M2 对照（inputs_embeds_len）

| cad_id | B0 | B1 | M2 |
|---|---:|---:|---:|
| deepcad__0005_00051866 | 184 | 194 | 194 |
| fusion360__63539_dd7fddaa_0005 | 4081 | 4088 | 4088 |
| fusion360__30400_8824ce97_0007 | 4081 | 4088 | 4088 |
| fusion360__109232_04340d62_0014 | 3975 | 3982 | 3982 |
| fusion360__50409_4a322fbf_0009 | 4081 | 4088 | 4088 |

B1==M2。B0 = M2-10（少 3 个 edge marker + 把 1 个 pad 换成 8 summary 的净 +7）。

len(labels)==attention_mask==inputs_embeds：五个样本三臂全部 True。
