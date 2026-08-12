"""
Pydantic models for the Agent WAF system.
Covers: policies, agent requests, rule evaluations, audit events, API responses.
"""
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import uuid


# ─── Policy Models ────────────────────────────────────────────────────────────

class RateLimitConfig(BaseModel):
    enabled: bool = True
    max_calls: int = Field(default=5, ge=1)
    window_seconds: int = Field(default=60, ge=1)


class ParameterValidationConfig(BaseModel):
    enabled: bool = True
    blocked_values: List[str] = Field(default_factory=list)
    max_parameter_size: int = Field(default=10000, ge=1)


class DataScopeConfig(BaseModel):
    enabled: bool = True
    allowed_scopes: Dict[str, List[str]] = Field(default_factory=dict)


class SequenceRuleItem(BaseModel):
    tool: str
    requires: str


class SequenceRulesConfig(BaseModel):
    enabled: bool = True
    rules: List[SequenceRuleItem] = Field(default_factory=list)


class PolicyDocument(BaseModel):
    agent_id: str = Field(..., min_length=1)
    enabled: bool = True
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    parameter_validation: ParameterValidationConfig = Field(
        default_factory=ParameterValidationConfig
    )
    data_scope: DataScopeConfig = Field(default_factory=DataScopeConfig)
    sequence_rules: SequenceRulesConfig = Field(default_factory=SequenceRulesConfig)
    tool_permissions: Dict[str, Dict[str, bool]] = Field(default_factory=dict)
    shadow_mode: bool = False
    version: int = Field(default=1, ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class PolicyCreateRequest(BaseModel):
    """Input model for creating a new policy."""
    agent_id: str = Field(..., min_length=1)
    enabled: bool = True
    rate_limit: RateLimitConfig = Field(default_factory=RateLimitConfig)
    parameter_validation: ParameterValidationConfig = Field(
        default_factory=ParameterValidationConfig
    )
    data_scope: DataScopeConfig = Field(default_factory=DataScopeConfig)
    sequence_rules: SequenceRulesConfig = Field(default_factory=SequenceRulesConfig)
    tool_permissions: Dict[str, Dict[str, bool]] = Field(default_factory=dict)
    shadow_mode: bool = False


class PolicyUpdateRequest(BaseModel):
    """Input model for updating a policy. All fields optional."""
    enabled: Optional[bool] = None
    rate_limit: Optional[RateLimitConfig] = None
    parameter_validation: Optional[ParameterValidationConfig] = None
    data_scope: Optional[DataScopeConfig] = None
    sequence_rules: Optional[SequenceRulesConfig] = None
    tool_permissions: Optional[Dict[str, Dict[str, bool]]] = None
    shadow_mode: Optional[bool] = None


# ─── Agent Request ────────────────────────────────────────────────────────────

class AgentRequest(BaseModel):
    agent_id: str = Field(..., min_length=1)
    session_id: str = Field(..., min_length=1)
    tool_name: str = Field(..., min_length=1)
    parameters: Dict[str, Any] = Field(default_factory=dict)
    request_id: Optional[str] = None


# ─── Rule Evaluation ─────────────────────────────────────────────────────────

class RuleEvaluation(BaseModel):
    rule: str
    status: str  # "PASS" or "FAIL"
    reason: Optional[str] = None


# ─── Audit Event ──────────────────────────────────────────────────────────────

class AuditEvent(BaseModel):
    event_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    request_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    agent_id: str
    session_id: str
    tool_name: str
    parameters: Dict[str, Any]  # sanitized before storage
    rule_evaluations: List[RuleEvaluation]
    final_disposition: str  # "ALLOW" or "BLOCK"
    mode: str = "ENFORCE"  # "ENFORCE" or "SHADOW"
    tool_result: Optional[Dict[str, Any]] = None
    latency_ms: float = 0
    policy_version: int = 0


# ─── API Responses ────────────────────────────────────────────────────────────

class ErrorDetail(BaseModel):
    code: str
    message: str


class ProxyResponse(BaseModel):
    success: bool
    decision: str  # "ALLOW" or "BLOCK"
    tool_name: str
    request_id: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[ErrorDetail] = None
    rule_evaluations: List[RuleEvaluation] = Field(default_factory=list)
    mode: str = "ENFORCE"


class DashboardSummary(BaseModel):
    total: int = 0
    allowed: int = 0
    blocked: int = 0
    block_rate: float = 0.0
    by_rule: Dict[str, int] = Field(default_factory=dict)


class PaginatedEvents(BaseModel):
    events: List[Dict[str, Any]]
    total: int
    limit: int
    offset: int
