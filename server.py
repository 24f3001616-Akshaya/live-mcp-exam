
import hashlib
import os

from mcp.server import MCPServer
from mcp.server.mcpserver import Context

EMAIL = "24f3001616@ds.study.iitm.ac.in".strip().lower()

mcp = MCPServer("Live Exam MCP Server")


@mcp.tool()
def solve_challenge(ctx: Context) -> str:
    """Solve the current exam challenge from the HTTP request headers."""
    headers = ctx.headers or {}
    challenge = headers.get("x-exam-challenge")

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge header")

    message = f"{challenge}:{EMAIL}"
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()

    return digest[:16]


if __name__ == "__main__":
    mcp.run(
        transport="streamable-http",
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
    )
