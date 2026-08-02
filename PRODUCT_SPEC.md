# EchoClause Product Spec (frozen R0)

## Scope

Single demo scenario: digital micro-loan sales promises vs. signed contract for fictional **Nuru Credit**.

## Inputs

1. Advertisement image — $1,000, 0% interest, no hidden fees, 30 days
2. Sales pitch audio + transcript
3. Support chat screenshot — no automatic debit
4. Contract page — $150 platform fee, $1,150 total, 5%/week late fee, 21 days, auto-debit

## Expected contradictions (gold.json)

Five frozen contradictions across platform fee, total repayment, late fee, term days, automatic debit.

## Architecture layers

1. Source ingestion (PNG/WAV)
2. Gemma claim extraction → SourceClaim
3. Deterministic normalization
4. Claim reconciliation → ComparisonResult
5. Evidence-grounded report

## Status vocabulary

SUPPORTED, CONTRADICTED, HIDDEN_IN_CONTRACT, AMBIGUOUS, MISSING_EVIDENCE, NEEDS_REVIEW

## Model strategy

Primary: `google/gemma-4-E4B-it` (max 2 load attempts)
Fallback: `google/gemma-4-E2B-it`

## Tools (allowlist)

normalize_financial_term, calculate_total_repayment, calculate_fee_percentage, compare_normalized_terms, generate_clarification_questions
