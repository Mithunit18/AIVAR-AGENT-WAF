import pytest
from utils.sanitizer import sanitize_parameters

def test_sanitize_basic():
    parameters = {"name": "Alice", "password": "secret_password", "token": "abc123xyz"}
    sanitized = sanitize_parameters(parameters)
    
    assert sanitized["name"] == "Alice"
    assert sanitized["password"] == "***REDACTED***"
    assert sanitized["token"] == "***REDACTED***"

def test_sanitize_nested():
    parameters = {
        "user": {
            "name": "Bob",
            "credentials": {
                "api_key": "my_secret_key"
            }
        }
    }
    sanitized = sanitize_parameters(parameters)
    
    assert sanitized["user"]["name"] == "Bob"
    # 'credentials' is a sensitive field, so the entire dict is replaced by ***REDACTED***
    assert sanitized["user"]["credentials"] == "***REDACTED***"

def test_sanitize_list():
    parameters = {
        "users": [
            {"name": "Charlie", "secret": "shh"},
            {"name": "Dave", "secret": "dont_tell"}
        ]
    }
    sanitized = sanitize_parameters(parameters)
    
    assert sanitized["users"][0]["name"] == "Charlie"
    assert sanitized["users"][0]["secret"] == "***REDACTED***"
    assert sanitized["users"][1]["secret"] == "***REDACTED***"

def test_sanitize_empty_and_null():
    parameters = {"key": None, "list": [], "dict": {}}
    sanitized = sanitize_parameters(parameters)
    
    assert sanitized == parameters
