"""
Policy Management API — CRUD endpoints for WAF policies.
All policy values are data, not code.
"""
from fastapi import APIRouter, Request, HTTPException
from models.schemas import PolicyCreateRequest, PolicyUpdateRequest

router = APIRouter()


@router.get("/")
async def list_policies(request: Request):
    """List all policies."""
    repo = request.app.state.policy_repo
    policies = await repo.get_all_policies()
    return {"policies": policies, "count": len(policies)}


@router.get("/{agent_id}")
async def get_policy(agent_id: str, request: Request):
    """Get a single policy by agent_id."""
    repo = request.app.state.policy_repo
    policy = await repo.get_policy(agent_id)
    if not policy:
        raise HTTPException(status_code=404, detail={
            "code": "POLICY_NOT_FOUND",
            "message": f"No policy found for agent: {agent_id}",
        })
    return policy


@router.post("/", status_code=201)
async def create_policy(policy: PolicyCreateRequest, request: Request):
    """Create a new policy."""
    repo = request.app.state.policy_repo
    try:
        created = await repo.create_policy(policy.model_dump())
        return created
    except ValueError as e:
        raise HTTPException(status_code=409, detail={
            "code": "POLICY_CONFLICT",
            "message": str(e),
        })


@router.put("/{agent_id}")
async def update_policy(agent_id: str, updates: PolicyUpdateRequest, request: Request):
    """Update an existing policy. Auto-increments version."""
    repo = request.app.state.policy_repo
    update_data = updates.model_dump(exclude_none=True)
    if not update_data:
        raise HTTPException(status_code=400, detail={
            "code": "EMPTY_UPDATE",
            "message": "No fields to update",
        })
    # Convert nested Pydantic models to dicts
    for key, value in update_data.items():
        if hasattr(value, "model_dump"):
            update_data[key] = value.model_dump()
    updated = await repo.update_policy(agent_id, update_data)
    if not updated:
        raise HTTPException(status_code=404, detail={
            "code": "POLICY_NOT_FOUND",
            "message": f"No policy found for agent: {agent_id}",
        })
    return updated


@router.delete("/{agent_id}")
async def delete_policy(agent_id: str, request: Request):
    """Delete a policy."""
    repo = request.app.state.policy_repo
    deleted = await repo.delete_policy(agent_id)
    if not deleted:
        raise HTTPException(status_code=404, detail={
            "code": "POLICY_NOT_FOUND",
            "message": f"No policy found for agent: {agent_id}",
        })
    return {"message": f"Policy for agent '{agent_id}' deleted", "success": True}
