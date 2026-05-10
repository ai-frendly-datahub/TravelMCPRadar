from __future__ import annotations

import json
import sys
from typing import Any


TOOL_NAMES = [
    "get_area_code",
    "get_detail_common",
    "search_tour_info",
]

TOOLS = [
    {
        "name": name,
        "title": name.replace("_", " ").title(),
        "description": f"Return deterministic Visit Korea fixture data for {name}.",
        "inputSchema": {"type": "object", "additionalProperties": True},
    }
    for name in TOOL_NAMES
]

TOOL_RESULTS = {
    name: {
        "title": f"Visit Korea {name} fixture",
        "url": f"https://example.test/travel/visit-korea/{name}",
        "summary": (
            "Fixture-only Visit Korea MCP result for Seoul. "
            "No third-party package, remote endpoint, or real Tour API was called."
        ),
        "repository": "pjookim/mcp-visit-korea",
        "tool_name": name,
        "fixture": True,
    }
    for name in TOOL_NAMES
}


def _response(request_id: Any, result: Any) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "result": result}


def _error(request_id: Any, code: int, message: str) -> dict[str, Any]:
    return {"jsonrpc": "2.0", "id": request_id, "error": {"code": code, "message": message}}


def handle(message: dict[str, Any]) -> dict[str, Any] | None:
    method = message.get("method")
    if method == "notifications/initialized":
        return None

    request_id = message.get("id")
    if method == "initialize":
        return _response(
            request_id,
            {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "serverInfo": {"name": "fake-visit-korea-mcp", "version": "0.0.0"},
            },
        )

    if method == "tools/list":
        return _response(request_id, {"tools": TOOLS})

    if method == "tools/call":
        params = message.get("params") or {}
        result = TOOL_RESULTS.get(str(params.get("name")))
        if result is None:
            return _error(request_id, -32602, "Unknown fixture tool")
        return _response(
            request_id,
            {
                "content": [
                    {
                        "type": "text",
                        "text": json.dumps(result, ensure_ascii=False, sort_keys=True),
                    }
                ],
                "structuredContent": result,
            },
        )

    return _error(request_id, -32601, "Unsupported fixture method")


def main() -> int:
    for raw in sys.stdin:
        raw = raw.strip()
        if not raw:
            continue
        try:
            message = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if not isinstance(message, dict):
            continue
        response = handle(message)
        if response is None:
            continue
        print(json.dumps(response, ensure_ascii=False), flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
