import pytest
from rules_engine.scope_enforcer import enforce_scope

@pytest.mark.asyncio
async def test_scope_allow():
    parameters = {"customer_id": "C101", "other": "data"}
    allowed = {"customer_id": ["C101", "C102"]}
    
    result = await enforce_scope(parameters, allowed)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_scope_block():
    parameters = {"customer_id": "C999"}
    allowed = {"customer_id": ["C101", "C102"]}
    
    result = await enforce_scope(parameters, allowed)
    assert result.status == "FAIL"
    assert "outside the allowed scope" in result.reason

@pytest.mark.asyncio
async def test_scope_nested_allow():
    parameters = {"filter": {"region": "US", "status": "active"}}
    allowed = {"filter.region": ["US", "EU"]}
    
    result = await enforce_scope(parameters, allowed)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_scope_nested_block():
    parameters = {"filter": {"region": "AP", "status": "active"}}
    allowed = {"filter.region": ["US", "EU"]}
    
    result = await enforce_scope(parameters, allowed)
    assert result.status == "FAIL"
    assert "outside the allowed scope" in result.reason

@pytest.mark.asyncio
async def test_scope_missing_param_allow():
    # If parameter is not provided, scope enforcement passes (it only restricts provided params)
    parameters = {"other": "data"}
    allowed = {"customer_id": ["C101"]}
    
    result = await enforce_scope(parameters, allowed)
    assert result.status == "PASS"
