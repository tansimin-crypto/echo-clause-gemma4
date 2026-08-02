"""Pydantic contracts for EchoClause MVP (frozen at R0)."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, Field


class ClaimField(str, Enum):
    PRINCIPAL = "principal"
    INTEREST_RATE = "interest_rate"
    PLATFORM_FEE = "platform_fee"
    PROCESSING_FEE = "processing_fee"
    TOTAL_REPAYMENT = "total_repayment"
    REPAYMENT_TERM_DAYS = "repayment_term_days"
    LATE_FEE = "late_fee"
    LATE_FEE_FREQUENCY = "late_fee_frequency"
    AUTOMATIC_DEBIT = "automatic_debit"
    AUTOMATIC_RENEWAL = "automatic_renewal"
    CANCELLATION_FEE = "cancellation_fee"
    PREPAYMENT_PENALTY = "prepayment_penalty"


class ComparisonStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    CONTRADICTED = "CONTRADICTED"
    HIDDEN_IN_CONTRACT = "HIDDEN_IN_CONTRACT"
    AMBIGUOUS = "AMBIGUOUS"
    MISSING_EVIDENCE = "MISSING_EVIDENCE"
    NEEDS_REVIEW = "NEEDS_REVIEW"


class SourceType(str, Enum):
    ADVERTISEMENT = "advertisement"
    SALES_AUDIO = "sales_audio"
    SUPPORT_CHAT = "support_chat"
    CONTRACT = "contract"
    OTHER = "other"


class SourceClaim(BaseModel):
    claim_id: str
    source_id: str
    source_type: SourceType
    field: ClaimField
    raw_value: str
    normalized_value: str | float | int | bool | None = None
    currency: str | None = None
    unit: str | None = None
    frequency: str | None = None
    polarity: Literal["positive", "negative", "neutral"] = "neutral"
    evidence_text: str
    page_number: int | None = None
    timestamp_start: float | None = None
    timestamp_end: float | None = None
    confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    explicitness: Literal["explicit", "implicit", "inferred"] = "explicit"
    needs_review: bool = False


class ComparisonResult(BaseModel):
    canonical_field: ClaimField
    promise_claim_ids: list[str]
    contract_claim_ids: list[str]
    status: ComparisonStatus
    severity: Literal["low", "medium", "high", "critical"] = "medium"
    deterministic_difference: str | None = None
    evidence_summary: str
    clarification_question: str | None = None


# --- Tool argument schemas ---


class NormalizeFinancialTermArgs(BaseModel):
    raw_text: str
    field: ClaimField
    currency_hint: str | None = None


class CalculateTotalRepaymentArgs(BaseModel):
    principal: float
    platform_fee: float = 0.0
    processing_fee: float = 0.0
    interest_rate_percent: float = 0.0
    currency: str = "NGN"


class CalculateFeePercentageArgs(BaseModel):
    fee_amount: float
    principal: float
    currency: str = "NGN"


class CompareNormalizedTermsArgs(BaseModel):
    promise_value: str | float | int | bool
    contract_value: str | float | int | bool
    field: ClaimField
    promise_evidence: str
    contract_evidence: str


class GenerateClarificationQuestionsArgs(BaseModel):
    comparisons: list[ComparisonResult]
    max_questions: int = Field(default=5, ge=1, le=20)


# --- Tool call envelope ---


class ToolCallRequest(BaseModel):
    name: Literal[
        "normalize_financial_term",
        "calculate_total_repayment",
        "calculate_fee_percentage",
        "compare_normalized_terms",
        "generate_clarification_questions",
    ]
    arguments: dict[str, Any]


class ToolCallTrace(BaseModel):
    raw_tool_call: dict[str, Any]
    tool_name: str
    validation_ok: bool
    validation_error: str | None = None
    output: dict[str, Any] | list[Any] | None = None


class GoldContradiction(BaseModel):
    id: str
    canonical_field: ClaimField
    promise_summary: str
    contract_summary: str
    expected_status: ComparisonStatus = ComparisonStatus.CONTRADICTED
    severity: Literal["low", "medium", "high", "critical"] = "high"


class DemoGold(BaseModel):
    case_id: str = "nuru_credit_demo"
    company: str = "Nuru Credit"
    disclaimer: str = (
        "EchoClause compares representations across supplied evidence. "
        "It does not provide legal advice or determine legal enforceability."
    )
    expected_contradictions: list[GoldContradiction]
    min_contradiction_count: int = 5


class ExtractionResult(BaseModel):
    claims: list[SourceClaim]
    raw_model_output: str
    parse_valid: bool
    needs_review: bool = False
    parse_error: str | None = None
