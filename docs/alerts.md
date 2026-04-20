# Alert Rules and Runbooks

> Alert config: `config/alert_rules.yaml` | Owner: team-oncall

![Alert Rules Overview](images/alert_rules.png)

---

## 1. High Latency P95

| Field | Value |
|---|---|
| **Severity** | P2 |
| **Condition** | `latency_p95_ms > 5000 for 30m` |
| **Type** | Symptom-based |
| **Owner** | team-oncall |
| **Impact** | Tail latency breaches SLO (target: P95 < 3000ms) |

### Diagnosis Steps

1. Open top slow traces in Langfuse (last 1h, filter by `latency_ms > 5000`)
2. Compare span durations: RAG span vs LLM span
3. Check if incident toggle `rag_slow` is active in `data/incidents.json`
4. Inspect logs for `event=agent_run` with high `latency_ms` field

### Mitigation

- Truncate long queries before RAG retrieval
- Switch to fallback retrieval source
- Reduce prompt size / context window

### Evidence: Before / After Fix

| Before | After |
|---|---|
| ![Before fix](images/before_fix.png) | ![After fix](images/after_fix.png) |

---

## 2. High Error Rate

| Field | Value |
|---|---|
| **Severity** | P1 |
| **Condition** | `error_rate_pct > 5 for 5m` |
| **Type** | Symptom-based |
| **Owner** | team-oncall |
| **Impact** | Users receive failed responses (HTTP 500) |

### Diagnosis Steps

1. Group logs in `data/logs.jsonl` by `error_type` field
2. Inspect failed traces in Langfuse (filter status=ERROR)
3. Determine failure origin: LLM call, RAG tool, or schema validation
4. Cross-reference `instrumental_proof.png` for spike timing

![Instrumental Proof](images/instrumental_proof.png)

### Mitigation

- Rollback latest deployment if sudden spike after release
- Disable the failing tool call
- Retry with fallback model

---

## 3. Cost Budget Spike

| Field | Value |
|---|---|
| **Severity** | P2 |
| **Condition** | `hourly_cost_usd > 2x_baseline for 15m` |
| **Type** | Symptom-based |
| **Owner** | finops-owner |
| **Impact** | Burn rate exceeds daily budget (target: < $2.5/day) |

### Diagnosis Steps

1. Split traces in Langfuse by `feature` and `model` tags
2. Compare `tokens_in` / `tokens_out` vs baseline
3. Check if `cost_spike` incident was injected (`scripts/inject_incident.py`)

### Mitigation

- Shorten system prompt and context window
- Route low-complexity requests to cheaper model
- Apply prompt caching for repeated context

---

## Alert Worksheet

| Alert Name | Severity | Condition Met? | Root Cause Identified | Resolved? |
|---|---|---|---|---|
| high_latency_p95 | P2 | [ ] | | [ ] |
| high_error_rate | P1 | [ ] | | [ ] |
| cost_budget_spike | P2 | [ ] | | [ ] |

> Fill in during the incident simulation exercise using `python scripts/inject_incident.py --scenario rag_slow`
