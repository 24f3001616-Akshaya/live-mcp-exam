
import hashlib
import os
from contextvars import ContextVar

import uvicorn
from mcp.server import MCPServer
from mcp.server.transport_security import TransportSecuritySettings

EMAIL = "24f3001616@ds.study.iitm.ac.in".strip().lower()

current_challenge = ContextVar("current_challenge", default=None)

mcp = MCPServer("Live Exam MCP Server")


class ChallengeHeaderMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope.get("headers", []))
        challenge = headers.get(b"x-exam-challenge")

        token = current_challenge.set(
            challenge.decode("ascii") if challenge else None
        )

        try:
            await self.app(scope, receive, send)
        finally:
            current_challenge.reset(token)


@mcp.tool()
def solve_challenge() -> str:
    """Solve the current exam challenge from the HTTP request headers."""

    challenge = current_challenge.get()

    if not challenge:
        raise ValueError("Missing X-Exam-Challenge HTTP header")

    message = f"{challenge}:{EMAIL}"
    digest = hashlib.sha256(message.encode("utf-8")).hexdigest()

    return digest[:16]


if __name__ == "__main__":
    security = TransportSecuritySettings(
        allowed_hosts=[
            "live-mcp-exam.onrender.com",
            "live-mcp-exam.onrender.com:*",
        ],
        allowed_origins=[
            "https://live-mcp-exam.onrender.com",
        ],
    )

    app = mcp.streamable_http_app(
        transport_security=security
    )

    app = ChallengeHeaderMiddleware(app)

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=int(os.environ.get("PORT", "10000")),
    )
