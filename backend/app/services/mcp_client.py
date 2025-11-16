# backend/app/services/mcp_client.py

class MCPClient:
    """
    Stub de cliente MCP.
    Más adelante, aquí se implementará la conexión real con los tools MCP.
    De momento, solo devuelve datos dummy o llama a funciones internas.
    """

    def call_tool(self, tool_name: str, payload: dict) -> dict:
        # Por ahora, solo loguea y devuelve lo mismo
        print(f"[MCPClient] Llamando al tool: {tool_name} con payload: {payload}")
        return {"tool": tool_name, "payload": payload}
