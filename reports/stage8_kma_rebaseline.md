# 阶段8 KMA 对齐重基线说明（B = DGXD01）— 2026-09-03

- 目的：基于已合入 master 的「更新数据格式」（PR #26：KMA 统一格式对齐，commit 419668f），重建阶段8（标注）工作基线，承接已关闭的 #25。
- 现状基线：master 含 schema.json kma_alignment/gold_enum_alignment、convert_to_schema.py KMA_ENUMS/KMA_LEGACY_MAP、evidence/source/kma_unified_data_format_FREEZE_V1/（KMA 标准 + D9 检索集已入库）。
- KMA 状态：FREEZE_PROPOSAL（未 FROZEN）；红线：FROZEN 前不强制阻断 processed 重转、不打断既有试标结论的引用。

## 一、旧 #25 与本次重基线的差异
| 维度 | 旧（#25，已关闭） | 新（本 PR，KMA 对齐） |
| --- | --- | --- |
| gold 字段 | 自创：preference_type/scope/confidence/should_store/operation 等 | canonical：Preference/Knowledge/Conflict/ForgetPlan/MemorySourceEvent 业务字段（gold_enum_alignment） |
| 枚举 | 旧词表（enum_dictionary legacy） | KMA §5 枚举 + legacy→KMA 映射层 |
| 生命周期 | review_status | review_status（评测层）+ gold.memory_status（业务层）职责分离 |
| 审计 | stage7_kma_b_audit.py | 保留并在 KMA 侧继续使用 |

## 二、阶段8 v2 目标 gold 对象（按 master schema gold_enum_alignment）
| 任务 | 目标 canonical 对象 | 关键字段（对齐 KMA） |
| --- | --- | --- |
| preference_extraction | Preference | preference_scope(global/topic/tool/session/time_window)、expression_type(explicit/implicit)、confidence_score(float[0,1])、should_persist/is_temporary(bool)、memory_status、version、evidence_event_ids |
| knowledge_retrieval | Knowledge | knowledge_type(6)、knowledge_id、memory_status、禁止召回 8 类、版本引用 memory_id+version_id |
| conflict_resolution | Conflict | conflict_type(5 KMA)、resolution_status(6)、left/right_knowledge_id、involved_knowledge_ids |
| precise_forgetting | ForgetPlan | forget_mode(5)、target_type(4)、status(7)、is_cascade/has_vector_cleanup/requires_confirmation |
| tool_result | MemorySourceEvent.source_business_status | source_business_status(8)、tool_call_id、失败不得写成成功 |
| end_to_end_session | MemorySourceEvent 链 | expected_memory 生命周期对齐 memory_status；expected_response 评测层 |

## 三、待 FROZEN/待裁定项（承接 worklog/20260903_KMA_FROZEN_pending_items.md）
1. preference_key 取值策略；2. app/task 语义落点；3. confidence 高/中/低→[0,1]；4. checkpoints 定位；5. LEGACY_MAP 核对；6. D9 已补档（#26 a3b20fa）；7. FROZEN 签署；8. 全量重转 processed + 重建标注产物。

## 四、本 PR 首批交付（待补充方向）
- 本说明（重基线依据与差异）；
- 后续按需加入：阶段8标注手册 v2（KMA 字段/枚举）、labels_A/B 骨架（canonical）、试标集引用（沿用 processed 样本池）、stage8_kappa/校验适配 KMA 一致字段集。

## 五、下一步
1. Reviewer 确认本重基线范围与 FROZEN 前不重转的边界；
2. A/B 就第 2 节目标 gold 对象逐任务对齐标注口径（可先行草案）；
3. FROZEN 后执行全量重转并按 v2 重建标注产物。
