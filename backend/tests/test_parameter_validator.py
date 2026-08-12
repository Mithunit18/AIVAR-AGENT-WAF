import pytest
from rules_engine.parameter_validator import validate_parameters

@pytest.mark.asyncio
async def test_parameter_allow():
    parameters = {"action": "update", "name": "John Doe"}
    blocked_values = ["delete", "DROP"]
    
    result = await validate_parameters(parameters, blocked_values, 1000)
    assert result.status == "PASS"

@pytest.mark.asyncio
async def test_parameter_block_exact():
    parameters = {"action": "delete"}
    blocked_values = ["delete", "DROP"]
    
    result = await validate_parameters(parameters, blocked_values, 1000)
    assert result.status == "FAIL"
    assert "Blocked parameter found" in result.reason

@pytest.mark.asyncio
async def test_parameter_block_substring():
    parameters = {"query": "SELECT * FROM users; DROP TABLE customers;"}
    blocked_values = ["delete", "DROP TABLE"]
    
    result = await validate_parameters(parameters, blocked_values, 1000)
    assert result.status == "FAIL"
    assert "Blocked parameter found" in result.reason

@pytest.mark.asyncio
async def test_parameter_size_limit():
    parameters = {"data": "A" * 1500}
    blocked_values = []
    
    result = await validate_parameters(parameters, blocked_values, max_parameter_size=1000)
    assert result.status == "FAIL"
    assert "exceeds maximum" in result.reason

@pytest.mark.asyncio
async def test_parameter_nested_dict():
    parameters = {"config": {"action": "delete"}}
    blocked_values = ["delete"]
    
    result = await validate_parameters(parameters, blocked_values, 1000)
    assert result.status == "FAIL"
    assert "Blocked parameter found" in result.reason
