# EchoClause Benchmark Results (R3/R4)

- Cases: **24**
- Mode: **recorded_replay** (recorded-claim replay, no live Gemma)

## Aggregate accuracy (status match per field)

| Method | Correct | Total | Accuracy |
|--------|---------|-------|----------|
| echo_clause | 27 | 28 | 96.4% |
| contract_only | 3 | 28 | 10.7% |
| text_concat | 23 | 28 | 82.1% |

## Per-case (echo_clause)

- `nuru_full_demo`: 1/1 (100%)
- `nuru_total_repayment`: 1/1 (100%)
- `nuru_late_fee`: 1/1 (100%)
- `nuru_term_days`: 1/1 (100%)
- `nuru_auto_debit`: 1/1 (100%)
- `syn_interest_match`: 1/1 (100%)
- `syn_principal_match`: 1/1 (100%)
- `syn_hidden_prepayment`: 1/1 (100%)
- `syn_missing_late_fee`: 1/1 (100%)
- `syn_processing_fee_mismatch`: 1/1 (100%)
- `syn_cancellation_hidden`: 1/1 (100%)
- `syn_auto_renewal_contradict`: 1/1 (100%)
- `syn_multi_field_1`: 2/2 (100%)
- `syn_multi_field_2`: 2/2 (100%)
- `syn_late_fee_freq`: 1/1 (100%)
- `syn_principal_high`: 1/1 (100%)
- `syn_debit_supported`: 0/1 (0%)
- `syn_platform_supported`: 1/1 (100%)
- `syn_term_supported`: 1/1 (100%)
- `syn_total_missing`: 1/1 (100%)
- `syn_interest_contradict`: 1/1 (100%)
- `syn_late_supported`: 1/1 (100%)
- `syn_hidden_auto_renewal`: 1/1 (100%)
- `syn_triple_field`: 3/3 (100%)

_Honest note: benchmark uses synthetic normalized claims (replay path). Live multimodal extraction is validated separately via R1 runtime spike._
