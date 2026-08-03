from pathlib import Path

import anyio
from mcp import ClientSession
from mcp.client.stdio import StdioServerParameters, stdio_client

from test_config import write_config


async def _scenario(project: Path, config_path: Path):
    params = StdioServerParameters(
        command=str(project / ".venv/bin/python"),
        args=["-m", "proofpay.mcp_server", "--config", str(config_path)],
        cwd=project,
    )
    async with stdio_client(params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()
            tools = await session.list_tools()
            assert [tool.name for tool in tools.tools] == [
                "create_invoice",
                "invoice_status",
                "release_artifact",
            ]
            result = await session.call_tool(
                "create_invoice",
                {"artifact_name": "sample.txt", "amount": "5", "buyer_label": "stdio-test"},
            )
            assert result.is_error is False
            assert result.structured_content["recipient"] == "11111111111111111111111111111111"
            assert "key" not in str(result.structured_content).lower()


def test_real_stdio_mcp_handshake_and_tool_call(tmp_path: Path):
    project = Path(__file__).parents[1]
    (tmp_path / "artifacts").mkdir()
    (tmp_path / "artifacts/sample.txt").write_text("paid work")
    config_path = tmp_path / "proofpay.toml"
    write_config(config_path, tmp_path)
    anyio.run(_scenario, project, config_path)
