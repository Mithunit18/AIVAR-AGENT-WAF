"""
WAF Proxy Endpoint — the central enforcement point.
Every tool invocation is intercepted, inspected, and decided here.
"""
import time
import uuid
import logging
from fastapi import APIRouter, Request, Response

from models.schemas import AgentRequest, AuditEvent, ProxyResponse, ErrorDetail, RuleEvaluation
from rules_engine.evaluator import evaluate_all_rules
from rules_engine.sequence_checker import record_tool_execution
from utils.sanitizer import sanitize_parameters
from exceptions import PolicyNotFoundError, ToolNotFoundError

router = APIRouter()
logger = logging.getLogger("agent_waf")


@router.post("/execute", response_model=ProxyResponse)
async def execute_tool(request_body: AgentRequest, req: Request, response: Response):
    """
    WAF proxy execute endpoint.

    Flow:
    1. Validate request
    2. Load policy (cached)
    3. Evaluate all rules
    4. ALLOW → execute tool → audit → respond
    5. BLOCK → audit → respond with 403-equivalent structured response
    """
    start_time = time.time()
    request_id = request_body.request_id or getattr(req.state, "request_id", str(uuid.uuid4()))

    redis_client = req.app.state.redis
    policy_repo = req.app.state.policy_repo
    audit_repo = req.app.state.audit_repo
    tool_registry = req.app.state.tool_registry
    event_broker = req.app.state.event_broker

    # 1. Load policy
    policy = await policy_repo.get_policy(request_body.agent_id)
    if not policy:
        raise PolicyNotFoundError(request_body.agent_id)

    if not policy.get("enabled", True):
        raise PolicyNotFoundError(request_body.agent_id)

    policy_version = policy.get("version", 1)

    # 2. Evaluate all rules
    rule_evaluations, final_disposition, mode = await evaluate_all_rules(
        policy=policy,
        agent_id=request_body.agent_id,
        session_id=request_body.session_id,
        tool_name=request_body.tool_name,
        parameters=request_body.parameters,
        redis_client=redis_client,
    )

    # 3. Execute tool if ALLOWED
    tool_result = None
    if final_disposition == "ALLOW":
        # Check tool exists
        handler = tool_registry.get(request_body.tool_name)
        if handler is None:
            raise ToolNotFoundError(request_body.tool_name)

        try:
            tool_result = await handler(request_body.parameters)
        except Exception as e:
            logger.error(f"tool_execution_failed tool={request_body.tool_name}: {e}")
            tool_result = {"error": "Tool execution failed"}

        # Record tool execution for sequence tracking (only on ALLOW)
        await record_tool_execution(
            redis_client,
            request_body.agent_id,
            request_body.session_id,
            request_body.tool_name,
        )

    # 4. Sanitize parameters for audit
    sanitized_params = sanitize_parameters(request_body.parameters)

    # 5. Calculate latency
    latency_ms = round((time.time() - start_time) * 1000, 2)

    # 6. Create audit event
    audit_event = AuditEvent(
        request_id=request_id,
        agent_id=request_body.agent_id,
        session_id=request_body.session_id,
        tool_name=request_body.tool_name,
        parameters=sanitized_params,
        rule_evaluations=rule_evaluations,
        final_disposition=final_disposition,
        mode=mode,
        tool_result=tool_result,
        latency_ms=latency_ms,
        policy_version=policy_version,
    )
    audit_dict = audit_event.model_dump()

    # 7. Write to MongoDB
    try:
        await audit_repo.write_event(audit_dict.copy())
    except Exception as e:
        logger.error(f"audit_write_failed: {e}")

    # 8. Publish to SSE dashboard
    # Remove _id if present from the copy
    sse_event = {k: v for k, v in audit_dict.items() if k != "_id"}
    await event_broker.publish(sse_event)

    # 9. Build response
    if final_disposition == "BLOCK":
        failed_reason = next(
            (e.reason for e in rule_evaluations if e.status == "FAIL"),
            "Blocked by policy",
        )
        response.status_code = 403
        return ProxyResponse(
            success=False,
            decision="BLOCK",
            tool_name=request_body.tool_name,
            request_id=request_id,
            error=ErrorDetail(
                code="WAF_POLICY_VIOLATION",
                message=failed_reason,
            ),
            rule_evaluations=rule_evaluations,
            mode=mode,
        )

    return ProxyResponse(
        success=True,
        decision="ALLOW",
        tool_name=request_body.tool_name,
        request_id=request_id,
        result=tool_result,
        rule_evaluations=rule_evaluations,
        mode=mode,
    )
