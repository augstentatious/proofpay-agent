import asyncio

from proofpay.mcp_server import ProofPayMcpApp


def test_mcp_app_exposes_narrow_typed_surface(service):
    app = ProofPayMcpApp(service, rpc=None)
    tools = app.tools()
    assert [tool.name for tool in tools] == [
        "create_invoice",
        "invoice_status",
        "release_paid_artifact",
    ]
    create_schema = tools[0].input_schema
    assert set(create_schema["properties"]) == {"artifact_name", "amount", "buyer_label"}
    assert "recipient" not in create_schema["properties"]
    assert "token_mint" not in create_schema["properties"]


def test_mcp_create_never_returns_secret_and_release_fails_closed(service):
    app = ProofPayMcpApp(service, rpc=None)
    created = asyncio.run(
        app.call(
            "create_invoice",
            {"artifact_name": "report.md", "amount": "12.50", "buyer_label": "buyer"},
        )
    )
    assert created.is_error is False
    assert "key" not in str(created.structured_content).lower()
    invoice_id = created.structured_content["invoice_id"]

    blocked = asyncio.run(app.call("release_paid_artifact", {"invoice_id": invoice_id}))
    assert blocked.is_error is True
    assert "not paid" in blocked.content[0].text
