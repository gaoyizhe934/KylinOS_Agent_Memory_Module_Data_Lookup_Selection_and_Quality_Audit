# -*- coding: utf-8 -*-
"""D1 A candidate batch 自检（candidate_only / NON_PRODUCTION）
检查: parse、身份字段、无 human_decision/final_label/gold、blind 泄漏token、
enum 合法性、负例结构、target/must_keep 不重叠、exact dup、Jaccard>0.85 送审清单。
"""
import json, os, re, sys

D = r"C:\Users\LYF\AppData\Local\Temp\opencode\wt_pr37\data\interim\d1_candidates_A_20260906"
FILES = ["preference_candidates.jsonl", "conflict_candidates.jsonl", "forgetting_candidates.jsonl"]
FORBIDDEN = ["expected", "design", "target_ids", "must_keep", "hard_negative", "negative",
             "resolution", "scope_target", "peer", "reviewer", "gold", "winner",
             "conflict_type", "forget_mode", "scenario_class", "candidate_event_refs", "generation"]
VALID_CT = {"contradiction", "temporal_inconsistency", "source_conflict", "preference_conflict", "scope_ambiguity"}
VALID_FM = {"single_item", "session", "topic", "time_window", "full_reset"}
NEG_CLASSES = {"non_conflict_hard_negative", "ambiguous_selector_negative"}
fails, warns = [], []
seen_blind = {}

def bigram(s):
    s = re.sub(r"\s+", "", s)
    return {s[i:i+2] for i in range(max(0, len(s) - 1))}

def jacc(a, b):
    A, B = bigram(a), bigram(b)
    if not A or not B:
        return 0.0
    return len(A & B) / len(A | B)

def norm(o):
    return json.dumps(o, ensure_ascii=False, sort_keys=True)

rows = []
for fn in FILES:
    p = os.path.join(D, fn)
    n = 0
    for line in open(p, encoding="utf-8"):
        line = line.strip()
        if not line:
            continue
        n += 1
        r = json.loads(line)
        rows.append((fn, r))
    print("parse ok", fn, n)

# identity / forbidden
for fn, r in rows:
    sid = r["sample_id"]
    for k in ["review_status", "dataset_stage"]:
        if r.get(k) != "candidate_only":
            fails.append((sid, "%s=%s" % (k, r.get(k))))
    if r.get("admission_status") != "NOT_ADMISSION_APPROVED":
        fails.append((sid, "admission_status"))
    if r.get("id_binding_status") != "NON_PRODUCTION":
        fails.append((sid, "id_binding_status"))
    if r.get("dataset_version") != "kylin_memory_candidate_v4.1":
        fails.append((sid, "dataset_version=%s" % r.get("dataset_version")))
    for k in ["human_decision", "final_label", "gold"]:
        if k in r:
            fails.append((sid, "contains %s" % k))
    dm = r.get("design_metadata", {})
    for f in ["scenario_spec_id", "scenario_family", "generation"]:
        if f not in dm:
            fails.append((sid, "dm missing %s" % f))
    g = dm.get("generation", {})
    for f in ["generation_id", "prompt_version", "seed", "model", "source"]:
        if f not in g:
            fails.append((sid, "gen missing %s" % f))
    if g.get("source") != "os_controlled_authored":
        fails.append((sid, "source layer"))
    # blind leak scan
    bv = r.get("blind_visible", {})
    bvs = norm(bv)
    for tok in FORBIDDEN:
        if tok in bvs:
            fails.append((sid, "blind leaks token: %s" % tok))

    t = r["task_type"]
    # enum legality
    dmc = dm.get("design_conflict_type")
    if t == "conflict_resolution":
        if dm.get("scenario_class") == "non_conflict_hard_negative":
            if dmc is not None:
                fails.append((sid, "negative should not carry design_conflict_type"))
        else:
            if dmc not in VALID_CT:
                fails.append((sid, "illegal/absent design_conflict_type=%s" % dmc))
    if t == "precise_forgetting":
        cls = dm.get("scenario_class")
        fm = dm.get("forget_mode")
        if cls == "ambiguous_selector_negative":
            if fm is not None:
                fails.append((sid, "negative should not carry forget_mode"))
            if any(k in dm for k in ["target_ids", "must_keep", "expected_residual_count"]):
                fails.append((sid, "negative should not carry selector/target fields"))
        else:
            if fm not in VALID_FM:
                fails.append((sid, "illegal/absent forget_mode=%s" % fm))
            tids = set(dm.get("target_ids", []))
            mk = set(dm.get("must_keep", []))
            if tids & mk:
                fails.append((sid, "target_ids intersects must_keep"))
            if not tids:
                fails.append((sid, "non-negative forgetting lacks target_ids"))
    # exact-dup blind
    nb = norm(r["blind_visible"])
    if nb in seen_blind:
        fails.append((sid, "exact-duplicate blind_visible with %s" % seen_blind[nb]))
    else:
        seen_blind[nb] = sid

ids = [r["sample_id"] for _, r in rows]
if len(ids) != len(set(ids)):
    fails.append(("", "sample_id not unique (total %d / uniq %d)" % (len(ids), len(set(ids)))))
if len(rows) != 218:
    fails.append(("", "total rows %d != 218" % len(rows)))

# near-dup Jaccard across all blind texts
texts = {}
for _, r in rows:
    texts[r["sample_id"]] = "".join(norm(r["blind_visible"]))
sids = list(texts)
near = []
for i in range(len(sids)):
    for j in range(i + 1, len(sids)):
        jv = jacc(texts[sids[i]], texts[sids[j]])
        if jv > 0.85:
            near.append((sids[i], sids[j], round(jv, 3)))

print("near-dup pairs >0.85:", len(near))
for a, b, v in near[:60]:
    print("  NEAR", a, b, v)

print("\nRESULT:", "FAIL(%d)" % len(fails) if fails else "PASS")
for f in fails[:80]:
    print("  FAIL", f)
sys.exit(1 if fails else 0)
