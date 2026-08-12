"""
Tool Registry — maps tool names to their handler functions.
WAF dispatches ALLOWED calls through this registry.
"""
import logging
from typing import Dict, Any, Callable, Awaitable, Optional

from tools import mock_tools

logger = logging.getLogger("agent_waf")

# Type alias for tool handler
ToolHandler = Callable[[Dict[str, Any]], Awaitable[Dict[str, Any]]]


class ToolRegistry:
    """Registry of available tools. Tools are registered at startup."""

    def __init__(self):
        self._tools: Dict[str, ToolHandler] = {}

    def register(self, name: str, handler: ToolHandler):
        """Register a tool handler."""
        self._tools[name] = handler
        logger.debug(f"tool_registered name={name}")

    def get(self, name: str) -> Optional[ToolHandler]:
        """Look up a tool by name."""
        return self._tools.get(name)

    async def execute(self, name: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a registered tool. Raises KeyError if not found."""
        handler = self._tools.get(name)
        if handler is None:
            raise KeyError(f"Tool not registered: {name}")
        return await handler(parameters)

    def list_tools(self) -> list[str]:
        """List all registered tool names."""
        return list(self._tools.keys())


def create_default_registry() -> ToolRegistry:
    """Create a registry with all default mock tools."""
    registry = ToolRegistry()
    registry.register("authenticate_user", mock_tools.authenticate_user)
    registry.register("crm_read", mock_tools.crm_read)
    registry.register("crm_update", mock_tools.crm_update)
    registry.register("crm_delete", mock_tools.crm_delete)
    registry.register("send_email", mock_tools.send_email)
    registry.register("delete_records", mock_tools.delete_records)
    logger.info(f"tool_registry_initialized tools={registry.list_tools()}")
    return registry
