"""Typed MCP adapter; operator policy remains below the model."""

import argparse
import json
from pathlib import Path
from typing import Any

import anyio
import mcp_types as types
from mcp.server.lowlevel import Server
from mcp.server.stdio import stdio_server

from .config import load_runtime
from .models import ProofPayError
from .rpc import SolanaRpc
from .service import ProofPayService


class ProofPayMcpApp:
    def __init__(self, service: ProofPayService, rpc: SolanaRpc | None):
        self.service = service
        self.rpc = rpc

    def tools(self) -> list[types.Tool]:
        invoice_id = {
            "type": "object",
            "properties": {"invoice_id": {"type": "string"}},
            "required": ["invoice_id"],
            "additionalProperties": False,
        }
        return [
            types.Tool(
                name="create_invoice",
                description="Encrypt an inbox artifact and create an operator-policy-locked Solana Pay invoice.",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "artifact_name": {"type": "string"},
                        "amount": {"type": "string"},
                        "buyer_label": {"type": "string"},
                    },
                    "required": ["artifact_name", "amount", "buyer_label"],
                    "additionalProperties": False,
                },
            ),
            types.Tool(name="invoice_status", description="Poll finalized Solana evidence for one invoice.", inputSchema=invoice_id),
            types.Tool(
                name="release_artifact",
                description="Materialize a plaintext release only after exact finalized payment.",
                inputSchema=invoice_id,
            ),
        ]

    async def call(self, name: str, arguments: dict[str, Any]) -> types.CallToolResult:
        try:
            allowed = {
                "create_invoice": {"artifact_name", "amount", "buyer_label"},
                "invoice_status": {"invoice_id"},
                "release_artifact": {"invoice_id"},
            }
            if name not in allowed:
                raise ProofPayError("unknown tool")
            unexpected = set(arguments) - allowed[name]
            if unexpected:
                raise ProofPayError(f"unexpected arguments: {', '.join(sorted(unexpected))}")
            if name == "create_invoice":
                result = self.service.create_invoice(**arguments).to_public_dict()
            elif name == "invoice_status":
                invoice_id = arguments["invoice_id"]
                if self.rpc is not None:
                    self.service.poll_payment(invoice_id, self.rpc)
                result = self.service.get_invoice(invoice_id).to_public_dict()
            elif name == "release_artifact":
                result = self.service.release(arguments["invoice_id"]).to_public_dict()
            else:
                raise ProofPayError("unknown tool")
            return types.CallToolResult(
                content=[types.TextContent(text=json.dumps(result, sort_keys=True))],
                structuredContent=result,
            )
        except (KeyError, TypeError, ProofPayError, ValueError) as exc:
            return types.CallToolResult(content=[types.TextContent(text=str(exc))], isError=True)


def build_server(app: ProofPayMcpApp) -> Server:
    async def list_tools(_context, _params):
        return types.ListToolsResult(tools=app.tools())

    async def call_tool(_context, params):
        return await app.call(params.name, params.arguments or {})

    return Server(
        "proofpay",
        version="0.1.0",
        description="Custody-minimized paid delivery over Solana Pay",
        on_list_tools=list_tools,
        on_call_tool=call_tool,
    )


async def serve(config_path: Path) -> None:
    service, rpc = load_runtime(config_path)
    server = build_server(ProofPayMcpApp(service, rpc))
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def main() -> None:
    parser = argparse.ArgumentParser(description="Run the ProofPay MCP server")
    parser.add_argument("--config", type=Path, required=True)
    args = parser.parse_args()
    anyio.run(serve, args.config)


if __name__ == "__main__":
    main()
